export type DocumentItem = {
  id: string;
  filename: string;
  language: string;
};

export type ChatRoom = {
  id: string;
  document_id: string;
  title: string;
};

export type ChatMessage = {
  role: string;
  content: string;
};
