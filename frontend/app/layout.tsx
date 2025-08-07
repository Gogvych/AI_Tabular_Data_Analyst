import './globals.css';

export const metadata = {
  title: 'AI Tabular Analyst',
  description: 'Analyze CSV/Excel using LangChain + Groq',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
