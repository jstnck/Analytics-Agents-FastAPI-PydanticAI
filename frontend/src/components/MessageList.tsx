'use client';

import { useEffect, useRef } from 'react';
import type { Message } from '@/lib/types';
import MetadataDisplay from './MetadataDisplay';

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg font-medium">Welcome to NBA Analytics</p>
          <p className="mt-2">Ask me anything about NBA teams, stats, games, and more!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-3 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200 text-gray-800'
            }`}
          >
            <div className="mb-1 text-xs font-semibold opacity-70">
              {message.role === 'user' ? 'You' : 'NBA Agent'}
            </div>
            <div className="whitespace-pre-wrap break-words">{message.content}</div>

            {/* Show metadata for assistant messages */}
            {message.role === 'assistant' && message.metadata && (
              <div className="mt-3">
                <MetadataDisplay metadata={message.metadata} />
              </div>
            )}

            {message.timestamp && (
              <div className="mt-2 text-xs opacity-60">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
