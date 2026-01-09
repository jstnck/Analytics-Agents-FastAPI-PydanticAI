# NBA Analytics Frontend

A simple Next.js chat interface for interacting with the NBA Analytics Agent backend.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The frontend will be available at: http://localhost:3000

### 3. Make Sure Backend is Running
The frontend needs the FastAPI backend to be running on http://localhost:8000

```bash
# In the backend directory
cd ../backend
uv run uvicorn app.main:app --reload
```

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Create production build
- `npm start` - Start production server (run `npm run build` first)
- `npm run lint` - Run ESLint

## Environment Variables

Create a `.env.local` file (already created):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Main chat page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── ChatInterface.tsx     # Main chat container with state
│   ├── MessageList.tsx       # Display messages
│   ├── MessageInput.tsx      # Input field and send button
│   └── MetadataDisplay.tsx   # Show SQL queries and metadata
└── lib/
    ├── api.ts                # API client for backend calls
    └── types.ts              # TypeScript type definitions
```

## Features

- Real-time chat interface with the NBA analytics agent
- Display user and assistant messages with different styling
- Show SQL queries and metadata returned by the agent
- Loading states and error handling
- Auto-scroll to latest messages
- Responsive design with Tailwind CSS

## Usage

1. Type your question in the text area at the bottom
2. Press **Enter** to send (or click the Send button)
3. Press **Shift+Enter** for a new line
4. View agent responses and expand SQL queries by clicking the arrow

## Example Questions

- "What teams are in the database?"
- "Show me the Lakers stats"
- "Which team has the most wins?"
- "What games are coming up?"

## Technology Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls
- **React Hooks** - State management

## Troubleshooting

### CORS Errors
Make sure the backend CORS settings include `http://localhost:3000`:
```python
# backend/app/config.py
allowed_origins: list[str] = ["http://localhost:3000"]
```

### Module Not Found Errors
Run `npm install` to ensure all dependencies are installed.

### Build Errors
Check that TypeScript types are correct and all imports are valid.

### Backend Connection Issues
1. Verify backend is running on http://localhost:8000
2. Check `.env.local` has the correct API URL
3. Test backend health: http://localhost:8000/api/v1/health
