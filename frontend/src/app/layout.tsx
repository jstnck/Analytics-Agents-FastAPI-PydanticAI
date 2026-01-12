import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NBA Analytics Agent',
  description: 'Chat with an AI agent to explore NBA statistics and data',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
