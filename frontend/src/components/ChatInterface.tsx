'use client';

import { useState, useEffect } from 'react';
import { useChat } from '@ai-sdk/react';
import { DefaultChatTransport } from 'ai';
import type { Message, ChartSpec } from '@/lib/types';
import { getUsage } from '@/lib/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ChartRenderer from './ChartRenderer';

interface ChatInterfaceProps {
  mode: 'demo' | 'admin';
  apiKey: string | null;
}

export default function ChatInterface({ mode, apiKey }: ChatInterfaceProps) {
  const [includeChart, setIncludeChart] = useState(false);
  const [currentChart, setCurrentChart] = useState<{
    spec: ChartSpec;
    type?: string;
  } | null>(null);
  const [usageInfo, setUsageInfo] = useState<{
    queries_remaining?: number;
    queries_limit?: number;
  } | null>(null);

  // Vercel AI SDK useChat hook
  const {
    messages,
    sendMessage,
    status,
    error,
  } = useChat({
    transport: new DefaultChatTransport({
      api: '/api/v1/chat/stream',
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
    }),
    onFinish: () => {
      // Refresh usage info after streaming completes
      if (mode === 'demo') {
        fetchUsage();
      }
    },
    onError: (error) => {
      console.error('Stream error:', error);
    },
  });

  const isLoading = status === 'streaming' || status === 'submitted';

  // Fetch usage info helper
  const fetchUsage = async () => {
    if (mode === 'demo') {
      try {
        const usage = await getUsage(apiKey);
        setUsageInfo({
          queries_remaining: usage.queries_remaining,
          queries_limit: usage.queries_limit,
        });
      } catch (err) {
        console.error('Failed to fetch usage:', err);
      }
    }
  };

  // Initial usage fetch
  useEffect(() => {
    fetchUsage();
  }, [mode, apiKey]);

  const handleSendMessage = async (content: string) => {
    // Optionally append chart request
    const messageToSend = includeChart
      ? `${content} (Please include a chart visualization if appropriate)`
      : content;

    // Send message using new parts format
    sendMessage({ 
      role: 'user', 
      parts: [{ type: 'text', text: messageToSend }] 
    });
  };

  // Helper to extract text content from message parts
  const getMessageContent = (msg: any): string => {
    if (msg.content) return msg.content;
    if (msg.parts) {
      return msg.parts
        .filter((part: any) => part.type === 'text')
        .map((part: any) => part.text)
        .join('');
    }
    return '';
  };

// Helper to extract chart data from messages
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];
    
    // Basic check for chart spec in the data parts of the last message
    if (lastMsg.role === 'assistant' && lastMsg.parts) {
       lastMsg.parts.forEach((part: any) => {
          if (part.type === 'data' && part.data) {
             const dataItem = part.data;
             if (dataItem && typeof dataItem === 'object') {
                 if (dataItem.chart_spec) {
                    setCurrentChart((prev) => ({
                       spec: dataItem.chart_spec,
                       type: prev?.type
                    }));
                 }
                 if (dataItem.chart_type) {
                    setCurrentChart((prev) => ({
                       spec: prev?.spec || ({} as ChartSpec),
                       type: typeof dataItem.chart_type === 'string' ? dataItem.chart_type : dataItem.chart_type.type
                    }));
                 }
             }
          }
       });
    }
  }, [messages]);

  // Convert useChat messages to our Message type for MessageList
  const formattedMessages: Message[] = messages.map((msg: any) => {
    // Extract data parts for metadata
    const dataParts = msg.parts ? msg.parts.filter((p: any) => p.type === 'data').map((p: any) => p.data) : [];
    const metadata = dataParts.length > 0 ? Object.assign({}, ...dataParts) : undefined;
    
    return {
        role: msg.role as 'user' | 'assistant',
        content: getMessageContent(msg),
        timestamp: msg.createdAt?.toISOString() || new Date().toISOString(),
        metadata: metadata,
    };
  });

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
            <strong>Error:</strong> {error.message}
          </div>
        )}

        {/* Messages area */}
        <MessageList messages={formattedMessages} />

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
          {isLoading && (
            <p className="text-xs text-blue-500 mt-1 animate-pulse">
              Streaming response...
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
