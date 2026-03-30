"use client";
import { useThemeStore } from "@/lib/themes/theme-store";

export default function DotGrid() {
  const showGrid = useThemeStore(s => s.theme.fx.gridDots);
  const accentColor = useThemeStore(s => s.theme.colors.accent);

  if (!showGrid) return null;

  // SVG dot pattern as background — pure CSS, zero JS
  const dotSvg = encodeURIComponent(`
    <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'>
      <circle cx='12' cy='12' r='1' fill='${accentColor}' opacity='0.07'/>
    </svg>
  `);

  return (
    <div
      className="fixed inset-0 z-0 pointer-events-none"
      style={{
        backgroundImage: `url("data:image/svg+xml,${dotSvg}")`,
        backgroundSize: "24px 24px",
        opacity: 1,
      }}
    />
  );
}
