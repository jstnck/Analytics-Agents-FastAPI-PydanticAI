// API client for communicating with the FastAPI backend

import axios from 'axios';
import type { ChatRequest, ChatResponse } from './types';

// Get API URL from environment variable, fallback to localhost
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Send a message to the NBA analytics agent
 *
 * @param message - The user's message/question
 * @param conversationId - Optional conversation ID for context
 * @param history - Optional conversation history for multi-turn context
 * @returns Promise with the agent's response
 */
export async function sendMessage(
  message: string,
  conversationId?: string,
  history?: Array<{ role: string; content: string }>
): Promise<ChatResponse> {
  const payload: ChatRequest = {
    message,
    conversation_id: conversationId,
    history,
  };

  const response = await axios.post<ChatResponse>(`${API_URL}/chat`, payload, {
    headers: {
      'Content-Type': 'application/json',
    },
  });

  return response.data;
}

/**
 * Check if the backend API is healthy
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await axios.get(`${API_URL}/health`);
  return response.data;
}
