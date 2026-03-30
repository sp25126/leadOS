import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ThemeId, ThemeConfig } from "./theme-config";
import { cosmicDark, nordIce, cyberTerminal } from "./theme-config";

const THEME_MAP: Record<ThemeId, ThemeConfig> = {
  cosmic: cosmicDark,
  nord:   nordIce,
  cyber:  cyberTerminal,
};

interface ThemeStore {
  themeId:  ThemeId;
  theme:    ThemeConfig;
  setTheme: (id: ThemeId) => void;
  cycleTheme: () => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      themeId: "cosmic",
      theme:   cosmicDark,

      setTheme: (id) => {
        const t = THEME_MAP[id];
        if (!t) return;
        set({ themeId: id, theme: t });
        applyThemeToCSSVars(t);
      },

      cycleTheme: () => {
        const order: ThemeId[] = ["cosmic", "nord", "cyber"];
        const current = get().themeId;
        const next = order[(order.indexOf(current) + 1) % order.length];
        get().setTheme(next);
      },
    }),
    {
      name: "leados-theme-v1",
      onRehydrateStorage: () => (state) => {
        if (state) applyThemeToCSSVars(state.theme);
      },
    }
  )
);

// Inject all theme tokens as CSS custom properties on :root
// This makes every CSS/Tailwind arbitrary value auto-adapt
export function applyThemeToCSSVars(t: ThemeConfig) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;

  // Colors
  root.style.setProperty("--c-bg",          t.colors.background);
  root.style.setProperty("--c-surface",      t.colors.surface);
  root.style.setProperty("--c-surface-alt",  t.colors.surfaceAlt);
  root.style.setProperty("--c-border",       t.colors.border);
  root.style.setProperty("--c-border-hover", t.colors.borderHover);
  root.style.setProperty("--c-accent",       t.colors.accent);
  root.style.setProperty("--c-accent-soft",  t.colors.accentSoft);
  root.style.setProperty("--c-accent-2",     t.colors.accentSecondary);
  root.style.setProperty("--c-accent-3",     t.colors.accentTertiary);
  root.style.setProperty("--c-text-1",       t.colors.textPrimary);
  root.style.setProperty("--c-text-2",       t.colors.textSecondary);
  root.style.setProperty("--c-text-3",       t.colors.textMuted);
  root.style.setProperty("--c-text-ghost",   t.colors.textGhost);
  root.style.setProperty("--c-success",      t.colors.success);
  root.style.setProperty("--c-error",        t.colors.error);
  root.style.setProperty("--c-warning",      t.colors.warning);
  root.style.setProperty("--c-grad-0",       t.colors.gradientPrimary[0]);
  root.style.setProperty("--c-grad-1",       t.colors.gradientPrimary[1]);
  root.style.setProperty("--c-grad-2",       t.colors.gradientPrimary[2]);

  // Shape
  root.style.setProperty("--r-card",   t.shape.cardRadius);
  root.style.setProperty("--r-input",  t.shape.inputRadius);
  root.style.setProperty("--r-btn",    t.shape.buttonRadius);
  root.style.setProperty("--r-nav",    t.shape.navRadius);
  root.style.setProperty("--r-badge",  t.shape.badgeRadius);

  // Typography
  root.style.setProperty("--font-display", t.typography.fontDisplay);
  root.style.setProperty("--font-body",    t.typography.fontBody);
  root.style.setProperty("--font-mono",    t.typography.fontMono);
  root.style.setProperty("--tracking-hero",t.typography.trackingHero);
  root.style.setProperty("--tracking-body",t.typography.trackingBody);

  // Motion
  root.style.setProperty("--ease-base",
    `cubic-bezier(${t.motion.easing.join(",")})`);
  root.style.setProperty("--dur-fast",  `${t.motion.durationFast}ms`);
  root.style.setProperty("--dur-base",  `${t.motion.durationBase}ms`);
  root.style.setProperty("--dur-slow",  `${t.motion.durationSlow}ms`);

  // FX
  root.style.setProperty("--card-shadow",   t.fx.cardShadow);
  root.style.setProperty("--accent-glow",   t.fx.accentGlow);
  root.style.setProperty("--btn-glow",      t.fx.buttonGlow);
  root.style.setProperty("--cursor-color",  t.fx.cursorColor);

  // Body classes for theme-specific CSS
  document.body.classList.remove("theme-cosmic", "theme-nord", "theme-cyber");
  document.body.classList.add(`theme-${t.id}`);
}
