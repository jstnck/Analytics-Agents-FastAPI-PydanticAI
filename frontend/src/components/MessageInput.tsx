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
    <div className="border-t border-border bg-card p-4">
      <div className="flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about NBA stats... (e.g., 'What are the Lakers stats?')"
          disabled={disabled}
          rows={2}
          className="flex-1 resize-none rounded-xl border border-border px-4 py-2 bg-background text-foreground focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none disabled:bg-muted disabled:cursor-not-allowed transition-all"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="rounded-full bg-primary px-6 py-2 text-primary-foreground font-medium hover:bg-primary/90 disabled:bg-muted disabled:text-muted-foreground disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? 'Sending...' : 'Send'}
        </button>
      </div>

      <div className="flex items-center justify-between mt-2">
        <p className="text-xs text-muted-foreground">
          Press Enter to send, Shift+Enter for new line
        </p>

        {/* Include chart checkbox */}
        <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer hover:text-primary transition-colors">
          <input
            type="checkbox"
            checked={includeChart}
            onChange={(e) => onToggleChart(e.target.checked)}
            className="w-4 h-4 text-primary border-border rounded focus:ring-primary focus:ring-2"
          />
          <span className="select-none">Include chart with answer</span>
        </label>
      </div>
    </div>
  );
}
