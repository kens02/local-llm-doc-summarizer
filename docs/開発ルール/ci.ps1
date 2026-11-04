<#
.SYNOPSIS
    模擬CIスクリプト（GitLab CI の代わりにローカルで build / test / format を実行する）

.DESCRIPTION
    1. restore : dotnet restore（パッケージの取得）
    2. build   : dotnet build
    3. test    : dotnet test（テストプロジェクトが無ければ SKIP）
    4. format  : dotnet format --verify-no-changes（書式違反の検出）

    実行するたびに次を記録します。
    - logs\<実行ID>\<ステップ名>.log : 各ステップの出力
    - logs\<実行ID>\for-ai.txt       : 失敗時、チャットAIに貼り付ける用の抜粋
    - ci-history.csv                 : 実行履歴（試験管理台帳への転記用）

    ci-history.csv の Attempt 列は「同じ issue で何回目の実行か」を表します。
    これが「人手往復回数」（エージェントなら自動で回る部分）の測定値になります。

    Windows PowerShell 5.1 / PowerShell 7 の両方で動作します。
    日本語を含むため、このファイルは「UTF-8（BOM付き）」で保存してください。

.PARAMETER Target
    対象のソリューション（.sln）またはプロジェクト（.csproj）のパス。
    省略時は、カレントフォルダの .sln（無ければ .csproj）を自動で探します。

.PARAMETER IssueId
    対応中の issue ID（例：ISSUE-001）。履歴の集計に使います。

.PARAMETER Mode
    実施区分。AI（AIあり）/ NoAI（AIなし）。履歴の集計に使います。

.PARAMETER FormatMode
    format ステップの範囲。whitespace（既定・高速）/ style / full。

.EXAMPLE
    .\ci.ps1 -IssueId ISSUE-001 -Mode AI

.EXAMPLE
    .\ci.ps1 -Target .\src\MappingTool.sln -IssueId ISSUE-002 -Mode NoAI -SkipRestore
#>
[CmdletBinding()]
param(
    [string]$Target = "",
    [string]$IssueId = "NO-ISSUE",
    [ValidateSet("AI", "NoAI")]
    [string]$Mode = "AI",
    [string]$Configuration = "Debug",
    [ValidateSet("whitespace", "style", "full")]
    [string]$FormatMode = "whitespace",
    [switch]$SkipRestore,
    [switch]$SkipTest,
    [switch]$SkipFormat,
    [int]$TailLines = 40,
    [string]$LogRoot = ".\logs",
    [string]$HistoryFile = ".\ci-history.csv"
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------
# 準備
# ---------------------------------------------------------------
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] dotnet コマンドが見つかりません。.NET SDK がインストールされているか確認してください。" -ForegroundColor Red
    exit 2
}

if ([string]::IsNullOrWhiteSpace($Target)) {
    $found = Get-ChildItem -Path . -Filter *.sln -File | Select-Object -First 1
    if (-not $found) {
        $found = Get-ChildItem -Path . -Filter *.csproj -File | Select-Object -First 1
    }
    if (-not $found) {
        Write-Host "[ERROR] .sln / .csproj が見つかりません。-Target で指定してください。" -ForegroundColor Red
        exit 2
    }
    $Target = $found.FullName
}
if (-not (Test-Path $Target)) {
    Write-Host "[ERROR] 指定された対象が存在しません: $Target" -ForegroundColor Red
    exit 2
}
$Target = (Resolve-Path $Target).Path
$targetDir = Split-Path -Parent $Target

$runId = (Get-Date).ToString("yyyyMMdd-HHmmss")
$runDir = Join-Path $LogRoot $runId
New-Item -ItemType Directory -Path $runDir -Force | Out-Null

$results = New-Object System.Collections.Generic.List[object]

# ---------------------------------------------------------------
# ステップ実行の共通関数
# ---------------------------------------------------------------
function Invoke-CiStep {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    $logFile = Join-Path $runDir ("{0}.log" -f $Name)
    Write-Host ""
    Write-Host ("===== [{0}] dotnet {1}" -f $Name, ($Arguments -join " ")) -ForegroundColor Cyan

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    # dotnet が標準エラーに出力しても停止しないよう、一時的に Continue にする
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & dotnet @Arguments 2>&1 | ForEach-Object { "$_" }
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $prev
    $sw.Stop()

    $output | Out-File -FilePath $logFile -Encoding utf8
    $output | ForEach-Object { Write-Host $_ }

    if ($exitCode -eq 0) { $status = "PASS" } else { $status = "FAIL" }
    $color = "Green"
    if ($status -eq "FAIL") { $color = "Red" }
    Write-Host ("----- [{0}] {1}（{2:N1} 秒）" -f $Name, $status, $sw.Elapsed.TotalSeconds) -ForegroundColor $color

    $results.Add([pscustomobject]@{
        Step     = $Name
        Status   = $status
        Seconds  = [math]::Round($sw.Elapsed.TotalSeconds, 1)
        ExitCode = $exitCode
        Log      = $logFile
    })
    return ($status -eq "PASS")
}

function Add-SkipResult {
    param([string]$Name, [string]$Reason)
    Write-Host ""
    Write-Host ("===== [{0}] SKIP（{1}）" -f $Name, $Reason) -ForegroundColor Yellow
    $results.Add([pscustomobject]@{
        Step     = $Name
        Status   = "SKIP"
        Seconds  = 0
        ExitCode = ""
        Log      = $Reason
    })
}

# ---------------------------------------------------------------
# パイプライン本体（失敗したら以降のステップは SKIP）
# ---------------------------------------------------------------
$ok = $true

# 1. restore
if ($SkipRestore) {
    Add-SkipResult -Name "restore" -Reason "-SkipRestore 指定"
} else {
    $ok = Invoke-CiStep -Name "restore" -Arguments @("restore", $Target)
}

# 2. build
if (-not $ok) {
    Add-SkipResult -Name "build" -Reason "前のステップが失敗"
} else {
    $ok = Invoke-CiStep -Name "build" -Arguments @("build", $Target, "-c", $Configuration, "--no-restore", "-nologo")
}

# 3. test（テストプロジェクトの有無を確認）
$testProjects = Get-ChildItem -Path $targetDir -Filter *.csproj -File -Recurse |
    Where-Object { Select-String -Path $_.FullName -Pattern "Microsoft.NET.Test.Sdk|<IsTestProject>\s*true" -Quiet }

if ($SkipTest) {
    Add-SkipResult -Name "test" -Reason "-SkipTest 指定"
} elseif (-not $ok) {
    Add-SkipResult -Name "test" -Reason "前のステップが失敗"
} elseif (-not $testProjects) {
    Add-SkipResult -Name "test" -Reason "テストプロジェクトが見つからない"
} else {
    $ok = Invoke-CiStep -Name "test" -Arguments @("test", $Target, "-c", $Configuration, "--no-build", "--nologo")
}

# 4. format（ビルド失敗時も書式チェック自体は可能だが、結果を見やすくするため同じ扱いにする）
if ($SkipFormat) {
    Add-SkipResult -Name "format" -Reason "-SkipFormat 指定"
} elseif (-not $ok) {
    Add-SkipResult -Name "format" -Reason "前のステップが失敗"
} else {
    $formatArgs = @("format")
    if ($FormatMode -ne "full") { $formatArgs += $FormatMode }
    $formatArgs += @($Target, "--verify-no-changes")
    $ok = Invoke-CiStep -Name "format" -Arguments $formatArgs
}

# ---------------------------------------------------------------
# 結果のまとめ
# ---------------------------------------------------------------
$failed = @($results | Where-Object { $_.Status -eq "FAIL" })
if ($failed.Count -eq 0) { $overall = "PASS" } else { $overall = "FAIL" }
$totalSeconds = [math]::Round((($results | Measure-Object -Property Seconds -Sum).Sum), 1)

# 同じ issue での通算実行回数（Attempt）
$attempt = 1
if (Test-Path $HistoryFile) {
    $past = @(Import-Csv -Path $HistoryFile | Where-Object { $_.IssueId -eq $IssueId })
    $attempt = $past.Count + 1
}

# 履歴の追記（1回の実行を1行で記録）
$stepStatus = @{}
foreach ($r in $results) { $stepStatus[$r.Step] = $r.Status }
$row = [pscustomobject]@{
    RunId        = $runId
    DateTime     = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    IssueId      = $IssueId
    Mode         = $Mode
    Attempt      = $attempt
    Overall      = $overall
    Restore      = $stepStatus["restore"]
    Build        = $stepStatus["build"]
    Test         = $stepStatus["test"]
    Format       = $stepStatus["format"]
    TotalSeconds = $totalSeconds
    Target       = $Target
}
$row | Export-Csv -Path $HistoryFile -Append -NoTypeInformation -Encoding UTF8

# チャットAIに貼り付ける用の抜粋（失敗時のみ）
$forAi = Join-Path $runDir "for-ai.txt"
if ($overall -eq "FAIL") {
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# 模擬CIが失敗しました。原因と修正案を教えてください。")
    $lines.Add("")
    foreach ($f in $failed) {
        $lines.Add(("## 失敗ステップ: {0}（終了コード {1}）" -f $f.Step, $f.ExitCode))
        $all = Get-Content -Path $f.Log -Encoding UTF8
        # エラー・警告行を優先し、無ければ末尾を使う
        $errs = @($all | Where-Object { $_ -match "error|エラー|Failed|失敗" } | Select-Object -Unique -First $TailLines)
        if ($errs.Count -eq 0) { $errs = @($all | Select-Object -Last $TailLines) }
        $lines.Add('```text')
        foreach ($e in $errs) { $lines.Add($e) }
        $lines.Add('```')
        $lines.Add("")
    }
    $lines.Add("※ 貼り付ける前に、社外秘の情報（パス名・固有名詞など）が含まれていないか確認すること。")
    $lines | Out-File -FilePath $forAi -Encoding utf8
}

# サマリ表示（PRテンプレートの「模擬CIの結果」に貼り付ける）
Write-Host ""
Write-Host "================ 模擬CI サマリ ================"
Write-Host ("実行ID   : {0}" -f $runId)
Write-Host ("issue    : {0}（{1}回目 / 区分 {2}）" -f $IssueId, $attempt, $Mode)
Write-Host ("対象     : {0}" -f $Target)
Write-Host ""
Write-Host ("{0,-8} {1,-6} {2,8} {3,6}" -f "Step", "Status", "Seconds", "Exit")
foreach ($r in $results) {
    Write-Host ("{0,-8} {1,-6} {2,8} {3,6}" -f $r.Step, $r.Status, $r.Seconds, $r.ExitCode)
}
Write-Host ""
$color = "Green"
if ($overall -eq "FAIL") { $color = "Red" }
Write-Host ("総合結果 : {0}（合計 {1} 秒）" -f $overall, $totalSeconds) -ForegroundColor $color
if ($overall -eq "FAIL") {
    Write-Host ("AI貼り付け用: {0}" -f $forAi) -ForegroundColor Yellow
}
Write-Host ("履歴     : {0}" -f $HistoryFile)
Write-Host "==============================================="

if ($overall -eq "PASS") { exit 0 } else { exit 1 }
