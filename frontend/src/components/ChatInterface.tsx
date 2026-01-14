'use client';

import { useState, useEffect, useRef } from 'react';
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
  const [messages, setMessages] = useState<Message[]>([]);
  const [includeChart, setIncludeChart] = useState(false);
  const [loading, setLoading] = useState(false);
  const [streamingStep, setStreamingStep] = useState<string | null>(null);
  const [currentChart, setCurrentChart] = useState<{
    spec: ChartSpec;
    type?: string;
  } | null>(null);
  const [usageInfo, setUsageInfo] = useState<{
    queries_remaining?: number;
    queries_limit?: number;
  } | null>(null);

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

  // Update current chart when messages change
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];

    if (lastMsg.role === 'assistant' && lastMsg.metadata) {
      if (lastMsg.metadata.chart_spec && lastMsg.metadata.chart_type) {
        setCurrentChart({
          spec: lastMsg.metadata.chart_spec,
          type: lastMsg.metadata.chart_type,
        });
      }
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (loading) return;

    // Optionally append chart request
    const messageToSend = includeChart
      ? `${content} (Please include a chart visualization if appropriate)`
      : content;

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: content,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setStreamingStep(null);

    try {
      // Call streaming endpoint
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        },
        body: JSON.stringify({
          message: messageToSend,
          history: messages.map(m => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      // Process SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE events (separated by \n\n)
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        for (const event of events) {
          if (!event.trim()) continue;

          // Parse SSE event (format: "data: {json}")
          const dataMatch = event.match(/^data: (.+)$/m);
          if (!dataMatch) continue;

          try {
            const data = JSON.parse(dataMatch[1]);

            if (data.type === 'step') {
              // Update streaming step indicator
              setStreamingStep(data.message);
            } else if (data.type === 'final') {
              // Add final assistant message
              const assistantMessage: Message = {
                role: 'assistant',
                content: data.message,
                timestamp: new Date().toISOString(),
                metadata: data.metadata,
              };
              setMessages(prev => [...prev, assistantMessage]);
              setStreamingStep(null);
            } else if (data.type === 'error') {
              throw new Error(data.message);
            }
          } catch (parseError) {
            console.error('Failed to parse SSE event:', parseError);
          }
        }
      }

      // Refresh usage info after successful response
      if (mode === 'demo') {
        fetchUsage();
      }
    } catch (error) {
      console.error('Chat error:', error);

      // Add error message
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setStreamingStep(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full bg-background court-pattern">
      {/* Left side: Chat interface */}
      <div className="flex flex-col w-full lg:w-2/5 border-r border-border">
        {/* Usage info banner for demo users */}
        {mode === 'demo' && usageInfo && (
          <div className="bg-primary/10 border-b border-primary/20 px-4 py-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-foreground font-medium">
                Demo Mode: {usageInfo.queries_remaining || 0} / {usageInfo.queries_limit || 3} queries remaining
              </span>
              {usageInfo.queries_remaining === 0 && (
                <span className="text-xs text-destructive font-semibold">Limit reached</span>
              )}
            </div>
          </div>
        )}

        {/* Messages area */}
        <MessageList messages={messages} />

        {/* Streaming step indicator */}
        {loading && streamingStep && (
          <div className="px-4 py-2 bg-assist-teal/10 border-t border-assist-teal/20">
            <div className="flex items-center space-x-2 text-sm text-assist-teal">
              <div className="animate-pulse">●</div>
              <span>{streamingStep}</span>
            </div>
          </div>
        )}

        {/* Input area */}
        <MessageInput
          onSend={handleSendMessage}
          disabled={loading}
          includeChart={includeChart}
          onToggleChart={setIncludeChart}
        />
      </div>

      {/* Right side: Chart panel */}
      <div className="hidden lg:flex lg:w-3/5 flex-col bg-card">
        <div className="border-b border-border px-4 py-3">
          <h2 className="font-display font-semibold text-foreground">Chart Visualization</h2>
          {loading && (
            <p className="text-xs text-primary mt-1 animate-pulse">
              Processing...
            </p>
          )}
        </div>

        <div className="flex-1 p-4 overflow-auto">
          {currentChart ? (
            <ChartRenderer chartSpec={currentChart.spec} chartType={currentChart.type} />
          ) : (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              <div className="text-center">
                <svg
                  className="w-16 h-16 mx-auto mb-4 text-muted"
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
