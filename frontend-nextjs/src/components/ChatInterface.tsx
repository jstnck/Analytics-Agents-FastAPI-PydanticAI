'use client';

import { useState, useEffect } from 'react';
import type { Message, ChartSpec } from '@/lib/types';
import { sendMessage, getUsage } from '@/lib/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ChartRenderer from './ChartRenderer';

interface ChatInterfaceProps {
  mode: 'demo' | 'admin';
  apiKey: string | null;
}

export default function ChatInterface({ mode, apiKey }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [includeChart, setIncludeChart] = useState(false);
  const [currentChart, setCurrentChart] = useState<{
    spec: ChartSpec;
    type?: string;
    timestamp?: string;
  } | null>(null);
  const [usageInfo, setUsageInfo] = useState<{
    queries_remaining?: number;
    queries_limit?: number;
  } | null>(null);

  // Fetch usage info for demo users
  useEffect(() => {
    const fetchUsage = async () => {
      if (mode === 'demo') {
        try {
          const usage = await getUsage(apiKey);
          setUsageInfo({
            queries_remaining: usage.queries_remaining,
            queries_limit: usage.queries_limit,
          });
        } catch (err) {
          console.error('Failed to fetch usage info:', err);
        }
      }
    };

    fetchUsage();
  }, [mode, apiKey]);

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

      // Optionally append chart request to the message
      const messageToSend = includeChart
        ? `${content} (Please include a chart visualization if appropriate)`
        : content;

      // Call the backend API with conversation history and auth
      const response = await sendMessage(messageToSend, conversationId, history, apiKey);

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Refresh usage info for demo users after successful query
      if (mode === 'demo') {
        try {
          const usage = await getUsage(apiKey);
          setUsageInfo({
            queries_remaining: usage.queries_remaining,
            queries_limit: usage.queries_limit,
          });
        } catch (err) {
          console.error('Failed to refresh usage info:', err);
        }
      }

      // Add assistant response to the chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        timestamp: response.timestamp,
        metadata: response.metadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update chart display if chart spec is present
      if (response.metadata?.chart_spec) {
        setCurrentChart({
          spec: response.metadata.chart_spec,
          type: response.metadata.chart_type,
          timestamp: response.timestamp,
        });
      }
    } catch (err: any) {
      console.error('Error sending message:', err);

      let errorMsg = 'Failed to send message. Please try again.';
      let chatErrorMsg = '❌ Sorry, I encountered an error. Please make sure the backend is running and try again.';

      // Handle rate limit errors
      if (err.response?.status === 429) {
        errorMsg = err.response.data?.detail || 'Rate limit exceeded. Please wait before trying again.';
        chatErrorMsg = `❌ ${errorMsg}`;

        // Refresh usage info for demo users
        if (mode === 'demo') {
          try {
            const usage = await getUsage(apiKey);
            setUsageInfo({
              queries_remaining: usage.queries_remaining,
              queries_limit: usage.queries_limit,
            });
          } catch (usageErr) {
            console.error('Failed to refresh usage info:', usageErr);
          }
        }
      } else if (err.response?.status === 401) {
        errorMsg = 'Invalid API key. Please check your credentials.';
        chatErrorMsg = `❌ ${errorMsg}`;
      } else if (err instanceof Error) {
        errorMsg = err.message;
      }

      setError(errorMsg);

      // Add error message to chat
      const errorMessage: Message = {
        role: 'assistant',
        content: chatErrorMsg,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Left side: Chat interface */}
      <div className="flex flex-col w-full lg:w-2/5 border-r border-gray-200">
        {/* Usage info banner for demo users */}
        {mode === 'demo' && usageInfo && (
          <div className="bg-blue-50 border-b border-blue-200 px-4 py-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-blue-700">
                Demo Mode: {usageInfo.queries_remaining || 0} / {usageInfo.queries_limit || 3} queries remaining
              </span>
              {usageInfo.queries_remaining === 0 && (
                <span className="text-xs text-red-600 font-semibold">Limit reached</span>
              )}
            </div>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Messages area */}
        <MessageList messages={messages} />

        {/* Input area */}
        <MessageInput
          onSend={handleSendMessage}
          disabled={isLoading}
          includeChart={includeChart}
          onToggleChart={setIncludeChart}
        />
      </div>

      {/* Right side: Chart panel */}
      <div className="hidden lg:flex lg:w-3/5 flex-col bg-white">
        <div className="border-b border-gray-200 px-4 py-3">
          <h2 className="font-semibold text-gray-800">Chart Visualization</h2>
          {currentChart?.timestamp && (
            <p className="text-xs text-gray-500 mt-1">
              Updated: {new Date(currentChart.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>

        <div className="flex-1 p-4 overflow-auto">
          {currentChart ? (
            <ChartRenderer chartSpec={currentChart.spec} chartType={currentChart.type} />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-400">
              <div className="text-center">
                <svg
                  className="w-16 h-16 mx-auto mb-4 text-gray-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                <p className="text-sm font-medium">No chart yet</p>
                <p className="text-xs mt-2">
                  Ask for a visualization to see charts here
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
