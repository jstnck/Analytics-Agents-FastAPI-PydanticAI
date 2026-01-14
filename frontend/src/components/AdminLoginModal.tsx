'use client';

import { useState } from 'react';

interface AdminLoginModalProps {
  onLogin: (apiKey: string) => void;
  onClose: () => void;
}

export default function AdminLoginModal({ onLogin, onClose }: AdminLoginModalProps) {
  const [apiKey, setApiKey] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }

    // Clear error and pass to parent
    setError(null);
    onLogin(apiKey.trim());
  };

  return (
    <div className="fixed inset-0 bg-foreground/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-2xl shadow-card-glow max-w-md w-full p-6 border border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-display font-bold text-foreground">Admin Login</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <p className="text-sm text-muted-foreground mb-4">
          Enter your API key to access unlimited queries and full features.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="apiKey" className="block text-sm font-medium text-foreground mb-2">
              API Key
            </label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value);
                setError(null);
              }}
              className="w-full px-4 py-2 border border-border rounded-xl bg-background text-foreground focus:ring-2 focus:ring-primary/20 focus:border-primary focus:outline-none transition-all"
              placeholder="Enter your API key"
              autoFocus
            />
            {error && (
              <p className="text-destructive text-sm mt-2">{error}</p>
            )}
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-border text-foreground rounded-full hover:bg-muted transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 transition-colors"
            >
              Login
            </button>
          </div>
        </form>

        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Don't have an API key? Contact the administrator to get access.
          </p>
        </div>
      </div>
    </div>
  );
}
