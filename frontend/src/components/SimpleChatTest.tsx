'use client';

import { useState } from 'react';
import ChartRenderer from './ChartRenderer';
import type { ChartSpec } from '@/lib/types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    sql_query?: string;
    chart_spec?: ChartSpec;
    chart_type?: string;
    data_summary?: Record<string, unknown>;
  };
}

export default function SimpleChatTest() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [includeChart, setIncludeChart] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    const messageToSend = includeChart
      ? `${userMessage} (Please include a chart visualization if appropriate)`
      : userMessage;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      // Call simple REST endpoint
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageToSend,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      console.log('🎯 RECEIVED FROM BACKEND:', data);
      console.log('   - Has metadata:', !!data.metadata);
      if (data.metadata) {
        console.log('   - Metadata keys:', Object.keys(data.metadata));
        console.log('   - Has chart_spec:', !!data.metadata.chart_spec);
        console.log('   - Has chart_type:', !!data.metadata.chart_type);
        console.log('   - Chart spec:', data.metadata.chart_spec);
      }

      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message,
        metadata: data.metadata,
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Simple Chat Test (No Vercel SDK)</h1>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 border rounded p-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div
              className={`inline-block max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border text-gray-800'
              }`}
            >
              <div className="font-semibold text-xs mb-1">
                {msg.role === 'user' ? 'You' : 'Assistant'}
              </div>
              <div className="whitespace-pre-wrap">{msg.content}</div>

              {/* Metadata Display */}
              {msg.role === 'assistant' && msg.metadata && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  {/* Chart */}
                  {msg.metadata.chart_spec && msg.metadata.chart_type && (
                    <div className="mb-4">
                      <div className="text-xs font-semibold mb-2 text-gray-700">
                        📊 Chart:
                      </div>
                      <div className="bg-white rounded p-4">
                        <ChartRenderer
                          chartSpec={msg.metadata.chart_spec}
                          chartType={msg.metadata.chart_type}
                        />
                      </div>
                    </div>
                  )}

                  {/* SQL Query */}
                  {msg.metadata.sql_query && (
                    <details className="text-xs">
                      <summary className="font-semibold cursor-pointer text-blue-600">
                        SQL Query
                      </summary>
                      <pre className="mt-2 bg-gray-900 text-gray-100 p-2 rounded overflow-x-auto">
                        {msg.metadata.sql_query}
                      </pre>
                    </details>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-center text-gray-500">
            <div className="animate-pulse">Thinking...</div>
          </div>
        )}
      </div>

      <div className="border-t pt-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask about NBA stats..."
            disabled={loading}
            className="flex-1 border rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>

        <label className="flex items-center gap-2 mt-2 text-sm">
          <input
            type="checkbox"
            checked={includeChart}
            onChange={(e) => setIncludeChart(e.target.checked)}
            className="w-4 h-4"
          />
          Include chart with answer
        </label>
      </div>
    </div>
  );
}
