"use client";
import "@fontsource/jetbrains-mono";
import "@fontsource/dm-sans";
import { useEffect, useState } from "react";
import { useThemeStore, applyThemeToCSSVars } from "@/lib/themes/theme-store";

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useThemeStore(s => s.theme);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    applyThemeToCSSVars(theme);
  }, [theme]);

  // Load fonts conditionally or globally
  useEffect(() => {
    // Fonts are now loaded at top-level
  }, []);

  // During SSR, render a clean structure.
  // After hydration, render the theme-aware container.
  if (!mounted) {
    return <div className="min-h-screen bg-black text-white">{children}</div>;
  }

  return (
    <div
      className={`min-h-screen antialiased overflow-x-hidden relative transition-colors duration-700 ${mounted ? `theme-${theme.id}` : ''}`}
      style={{
        background: mounted ? "var(--c-bg)" : "#000000",
        color: mounted ? "var(--c-text-1)" : "#ffffff",
        fontFamily: mounted ? "var(--font-body)" : "inherit"
      }}
      data-theme-mounted={mounted}
    >
      {children}
    </div>
  );
}
