'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import LandingPage from '@/components/LandingPage';
import AdminLoginModal from '@/components/AdminLoginModal';
import { Logo } from '@/components/Logo';

type AppMode = 'landing' | 'demo' | 'admin';

export default function Home() {
  const [mode, setMode] = useState<AppMode>('landing');
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);

  const handleStartDemo = () => {
    setMode('demo');
  };

  const handleStartAdmin = () => {
    setShowAdminModal(true);
  };

  const handleAdminLogin = (key: string) => {
    setApiKey(key);
    setMode('admin');
    setShowAdminModal(false);
  };

  const handleBackToLanding = () => {
    setMode('landing');
    setApiKey(null);
  };

  // Show landing page
  if (mode === 'landing') {
    return (
      <>
        <LandingPage onStartDemo={handleStartDemo} onStartAdmin={handleStartAdmin} />
        {showAdminModal && (
          <AdminLoginModal
            onLogin={handleAdminLogin}
            onClose={() => setShowAdminModal(false)}
          />
        )}
      </>
    );
  }

  // Show chat interface for demo or admin mode
  return (
    <main className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="container mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Logo size="sm" />
              <div className="hidden sm:block border-l border-border pl-4">
                <p className="text-xs text-muted-foreground">
                  Ask questions about NBA teams, statistics, games, and more
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {mode === 'demo' && (
                <span className="pill-badge text-xs">
                  Demo Mode
                </span>
              )}
              {mode === 'admin' && (
                <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-assist-teal/10 border border-assist-teal/20 text-assist-teal">
                  Admin Mode
                </span>
              )}
              <button
                onClick={handleBackToLanding}
                className="text-sm bg-muted hover:bg-muted/80 text-foreground px-4 py-2 rounded-full transition-colors font-medium"
              >
                ← Back
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Interface */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface mode={mode} apiKey={apiKey} />
      </div>

      {/* Footer */}
      <footer className="bg-card text-muted-foreground text-xs py-2 px-6 text-center border-t border-border">
        Powered by PydanticAI & FastAPI
      </footer>
    </main>
  );
}
