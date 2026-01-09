'use client';

import { useState, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  includeChart: boolean;
  onToggleChart: (value: boolean) => void;
}

export default function MessageInput({
  onSend,
  disabled = false,
  includeChart,
  onToggleChart,
}: MessageInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter, new line on Shift+Enter
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about NBA stats... (e.g., 'What are the Lakers stats?')"
          disabled={disabled}
          rows={2}
          className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="rounded-lg bg-blue-600 px-6 py-2 text-white font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? 'Sending...' : 'Send'}
        </button>
      </div>

      <div className="flex items-center justify-between mt-2">
        <p className="text-xs text-gray-500">
          Press Enter to send, Shift+Enter for new line
        </p>

        {/* Include chart checkbox */}
        <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer hover:text-gray-900">
          <input
            type="checkbox"
            checked={includeChart}
            onChange={(e) => onToggleChart(e.target.checked)}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <span className="select-none">Include chart with answer</span>
        </label>
      </div>
    </div>
  );
}
