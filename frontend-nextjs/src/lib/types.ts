// TypeScript types for the NBA Analytics chat application

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  sql_query?: string;
  data_summary?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  history?: Array<{
    role: string;
    content: string;
  }>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  timestamp: string;
  metadata?: MessageMetadata;
}
