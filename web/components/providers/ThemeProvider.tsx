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

  // Wait for client-side hydration
  if (!mounted) {
    return <div className="min-h-screen bg-black text-white antialiased theme-cosmic">{children}</div>;
  }

  return (
    <div
      className={`min-h-screen antialiased overflow-x-hidden relative transition-colors duration-700 ${mounted ? `theme-${theme.id}` : ''}`}
      style={{
        background: "var(--c-bg)",
        color: "var(--c-text-1)",
        fontFamily: "var(--font-body)"
      }}
      data-theme-mounted={mounted}
    >
      {children}
    </div>
  );
}
