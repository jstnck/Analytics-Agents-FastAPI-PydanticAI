'use client';

import { useState } from 'react';
import type { Message } from '@/lib/types';
import { sendMessage } from '@/lib/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async (content: string) => {
    // Add user message to the chat
    const userMessage: Message = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Build conversation history from existing messages (exclude metadata for API)
      const history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Call the backend API with conversation history
      const response = await sendMessage(content, conversationId, history);

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response to the chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp,
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError(
        err instanceof Error ? err.message : 'Failed to send message. Please try again.'
      );

      // Add error message to chat
      const errorMessage: Message = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please make sure the backend is running and try again.',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Error banner */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Messages area */}
      <MessageList messages={messages} />

      {/* Input area */}
      <MessageInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
