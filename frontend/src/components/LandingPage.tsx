'use client';

import { Logo } from './Logo';

interface LandingPageProps {
  onStartDemo: () => void;
  onStartAdmin: () => void;
}

export default function LandingPage({ onStartDemo, onStartAdmin }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-background court-pattern">
      {/* Hero Section */}
      <section className="pt-20 pb-12 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row items-center gap-12 mb-16">
            <div className="flex-1 text-center md:text-left">
              <div className="mb-6 justify-center md:justify-start flex">
                <Logo size="lg" className="float-animation" />
              </div>
              <p className="text-xl text-muted-foreground leading-relaxed max-w-2xl">
                Natural language analytics for basketball data. Ask questions in plain English and get instant insights with visualizations.
              </p>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="stat-card rounded-2xl p-6">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="font-display text-lg text-foreground mb-2">SQL Generation</h3>
              <p className="text-sm text-muted-foreground">
                Automatic query generation from natural language
              </p>
            </div>

            <div className="stat-card rounded-2xl p-6">
              <div className="w-12 h-12 bg-assist-teal/10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="font-display text-lg text-foreground mb-2">Visualizations</h3>
              <p className="text-sm text-muted-foreground">
                Interactive charts and data exploration
              </p>
            </div>

            <div className="stat-card rounded-2xl p-6">
              <div className="w-12 h-12 bg-victory-gold/20 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="font-display text-lg text-foreground mb-2">Multi-Agent</h3>
              <p className="text-sm text-muted-foreground">
                Orchestrated agents for complex queries
              </p>
            </div>

            <div className="stat-card rounded-2xl p-6">
              <div className="w-12 h-12 bg-secondary/30 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">💬</span>
              </div>
              <h3 className="font-display text-lg text-foreground mb-2">Context Aware</h3>
              <p className="text-sm text-muted-foreground">
                Maintains conversation history
              </p>
            </div>
          </div>

          {/* Action Cards */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Demo Mode */}
            <div className="stat-card rounded-2xl p-8">
              <div className="mb-4">
                <span className="pill-badge mb-3">
                  Try it free
                </span>
                <h2 className="font-display text-2xl text-foreground mb-2">
                  Demo Mode
                </h2>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Test the analytics agent with 3 free queries. No login required.
              </p>
              <ul className="text-sm text-muted-foreground space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                  3 queries per hour
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                  SQL & visualizations
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
                  No account needed
                </li>
              </ul>
              <button
                onClick={onStartDemo}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-medium py-3 px-6 rounded-full transition-colors"
              >
                Start Demo
              </button>
            </div>

            {/* Admin Mode */}
            <div className="stat-card rounded-2xl p-8">
              <div className="mb-4">
                <span className="inline-block px-3 py-1 bg-secondary text-secondary-foreground text-xs font-medium rounded-full mb-3">
                  Full access
                </span>
                <h2 className="font-display text-2xl text-foreground mb-2">
                  Admin Mode
                </h2>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                For portfolio administrators with API key access.
              </p>
              <ul className="text-sm text-muted-foreground space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-secondary-foreground rounded-full"></span>
                  Unlimited queries
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-secondary-foreground rounded-full"></span>
                  Advanced features
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-secondary-foreground rounded-full"></span>
                  API key required
                </li>
              </ul>
              <button
                onClick={onStartAdmin}
                className="w-full bg-secondary-foreground text-white hover:bg-secondary-foreground/90 font-medium py-3 px-6 rounded-full transition-colors"
              >
                Admin Login
              </button>
            </div>

            {/* Notebooks */}
            <div className="stat-card rounded-2xl p-8 bg-gradient-ball text-white">
              <div className="mb-4">
                <span className="inline-block px-3 py-1 bg-white/20 text-white text-xs font-medium rounded-full mb-3">
                  Interactive
                </span>
                <h2 className="font-display text-2xl mb-2">
                  Notebooks
                </h2>
              </div>
              <p className="text-sm text-white/90 mb-4">
                Explore data with direct SQL queries in a reactive notebook environment.
              </p>
              <ul className="text-sm text-white/90 space-y-2 mb-6">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                  Execute SQL directly
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                  Call AI agents
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                  Powered by marimo
                </li>
              </ul>
              <a
                href="/notebooks/"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full bg-white text-primary hover:bg-white/90 font-medium py-3 px-6 rounded-full transition-colors text-center mb-3"
              >
                Open Notebook
              </a>
              <a
                href="http://localhost:8082"
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center text-sm text-white/80 hover:text-white transition-colors underline"
              >
                Edit Mode (Development)
              </a>
            </div>
          </div>

          {/* Tech Stack */}
          <div className="mt-16 pt-8 border-t border-border">
            <p className="text-xs text-muted-foreground text-center mb-4 uppercase tracking-wider">
              Built with
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <span className="text-xs bg-card text-foreground px-4 py-2 rounded-full border border-border">
                FastAPI
              </span>
              <span className="text-xs bg-card text-foreground px-4 py-2 rounded-full border border-border">
                PydanticAI
              </span>
              <span className="text-xs bg-card text-foreground px-4 py-2 rounded-full border border-border">
                DuckDB
              </span>
              <span className="text-xs bg-card text-foreground px-4 py-2 rounded-full border border-border">
                marimo
              </span>
              <span className="text-xs bg-card text-foreground px-4 py-2 rounded-full border border-border">
                Next.js
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
