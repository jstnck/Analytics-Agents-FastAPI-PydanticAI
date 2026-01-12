'use client';

interface LandingPageProps {
  onStartDemo: () => void;
  onStartAdmin: () => void;
}

export default function LandingPage({ onStartDemo, onStartAdmin }: LandingPageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl w-full bg-white rounded-lg shadow-xl p-8 md:p-12">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            NBA Analytics Agent
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Natural language analytics powered by Claude Haiku
          </p>
          <p className="text-sm text-gray-500">
            Ask questions about NBA data in plain English
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-semibold">📊</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">SQL Generation</h3>
              <p className="text-sm text-gray-600">
                Automatic query generation from natural language
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-green-600 font-semibold">📈</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Visualizations</h3>
              <p className="text-sm text-gray-600">Interactive charts powered by Plotly</p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-purple-600 font-semibold">🤖</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Multi-Agent System</h3>
              <p className="text-sm text-gray-600">
                Orchestrator coordinates SQL and visualization agents
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-yellow-600 font-semibold">💬</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Context Aware</h3>
              <p className="text-sm text-gray-600">
                Maintains conversation history across queries
              </p>
            </div>
          </div>
        </div>

        {/* Demo Section */}
        <div className="border-t border-gray-200 pt-8">
          <div className="bg-blue-50 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Try Demo Mode
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Test the analytics agent with 3 free queries. No login required.
            </p>
            <ul className="text-sm text-gray-600 space-y-1 mb-4">
              <li>• 3 queries per hour (IP-based)</li>
              <li>• Basic analytics and SQL queries</li>
              <li>• Chart visualizations included</li>
            </ul>
            <button
              onClick={onStartDemo}
              className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors"
            >
              Start Demo
            </button>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Admin Mode</h2>
            <p className="text-sm text-gray-600 mb-4">
              For portfolio administrators with API key access.
            </p>
            <button
              onClick={onStartAdmin}
              className="w-full md:w-auto bg-gray-700 hover:bg-gray-800 text-white font-semibold py-3 px-8 rounded-lg transition-colors"
            >
              Admin Login
            </button>
          </div>
        </div>

        {/* Tech Stack Badge */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center mb-2">Built with</p>
          <div className="flex flex-wrap justify-center gap-2">
            <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              FastAPI
            </span>
            <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              PydanticAI
            </span>
            <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              Claude Haiku
            </span>
            <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              DuckDB
            </span>
            <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              Next.js
            </span>
            <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              nginx
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
