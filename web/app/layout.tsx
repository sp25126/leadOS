import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "LeadOS Hub",
  description: "Next-gen Lead Generation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth" style={{
      "--c-bg": "#000000",
      "--c-surface": "#0a0a0a",
      "--c-surface-alt": "#111111",
      "--c-border": "rgba(255,255,255,0.06)",
      "--c-accent": "#7B2FFF",
      "--c-text-1": "#ffffff",
      "--font-display": "inherit",
      "--font-body": "sans-serif",
    } as any}>
      <body className={`${inter.variable} font-sans bg-black text-white antialiased theme-cosmic`}>
        {children}
      </body>
    </html>
  );
}
