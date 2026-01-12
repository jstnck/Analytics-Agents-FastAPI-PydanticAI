// API client for communicating with the FastAPI backend

import axios from 'axios';
import type { ChatRequest, ChatResponse } from './types';

// Get API URL from environment variable, fallback to localhost
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Get authorization headers for API requests
 */
function getAuthHeaders(apiKey?: string | null): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  return headers;
}

/**
 * Send a message to the NBA analytics agent
 *
 * @param message - The user's message/question
 * @param conversationId - Optional conversation ID for context
 * @param history - Optional conversation history for multi-turn context
 * @param apiKey - Optional API key for admin access
 * @returns Promise with the agent's response
 */
export async function sendMessage(
  message: string,
  conversationId?: string,
  history?: Array<{ role: string; content: string }>,
  apiKey?: string | null
): Promise<ChatResponse> {
  const payload: ChatRequest = {
    message,
    conversation_id: conversationId,
    history,
  };

  const response = await axios.post<ChatResponse>(`${API_URL}/chat`, payload, {
    headers: getAuthHeaders(apiKey),
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

/**
 * Get usage information for the current user
 *
 * @param apiKey - Optional API key for admin access
 * @returns Promise with usage information
 */
export async function getUsage(apiKey?: string | null): Promise<{
  tier: string;
  queries_used?: number;
  queries_remaining?: number;
  queries_limit?: number;
  limits?: string;
  message?: string;
}> {
  const response = await axios.get(`${API_URL}/usage`, {
    headers: getAuthHeaders(apiKey),
  });
  return response.data;
}
