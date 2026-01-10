'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import LandingPage from '@/components/LandingPage';
import AdminLoginModal from '@/components/AdminLoginModal';

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
    <main className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-blue-600 text-white py-4 px-6 shadow-md">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">NBA Analytics Agent</h1>
            <p className="text-sm text-blue-100 mt-1">
              Ask questions about NBA teams, statistics, games, and more
            </p>
          </div>
          <div className="flex items-center gap-4">
            {mode === 'demo' && (
              <span className="text-xs bg-blue-500 px-3 py-1 rounded-full">
                Demo Mode
              </span>
            )}
            {mode === 'admin' && (
              <span className="text-xs bg-green-500 px-3 py-1 rounded-full">
                Admin Mode
              </span>
            )}
            <button
              onClick={handleBackToLanding}
              className="text-sm bg-blue-500 hover:bg-blue-400 px-4 py-2 rounded transition-colors"
            >
              ← Back
            </button>
          </div>
        </div>
      </header>

      {/* Chat Interface */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface mode={mode} apiKey={apiKey} />
      </div>

      {/* Footer */}
      <footer className="bg-gray-100 text-gray-600 text-xs py-2 px-6 text-center border-t border-gray-200">
        Powered by PydanticAI & FastAPI
      </footer>
    </main>
  );
}
