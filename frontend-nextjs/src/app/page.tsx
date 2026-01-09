import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <main className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-blue-600 text-white py-4 px-6 shadow-md">
        <h1 className="text-2xl font-bold">NBA Analytics Agent</h1>
        <p className="text-sm text-blue-100 mt-1">
          Ask questions about NBA teams, statistics, games, and more
        </p>
      </header>

      {/* Chat Interface */}
      <div className="flex-1 overflow-hidden">
        <ChatInterface />
      </div>

      {/* Footer */}
      <footer className="bg-gray-100 text-gray-600 text-xs py-2 px-6 text-center border-t border-gray-200">
        Powered by PydanticAI & FastAPI
      </footer>
    </main>
  );
}
