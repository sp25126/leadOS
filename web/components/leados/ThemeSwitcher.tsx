"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useThemeStore } from "@/lib/themes/theme-store";
import { THEMES } from "@/lib/themes/theme-config";
import type { ThemeId } from "@/lib/themes/theme-config";
import { Palette, Check, X } from "lucide-react";

// Mini theme preview card
function ThemePreviewCard({
  theme,
  isActive,
  onSelect,
  onPreview,
  onPreviewEnd,
}: {
  theme: typeof THEMES[0];
  isActive: boolean;
  onSelect: () => void;
  onPreview: () => void;
  onPreviewEnd: () => void;
}) {
  return (
    <motion.button
      whileTap={{ scale: 0.96 }}
      onClick={onSelect}
      onMouseEnter={onPreview}
      onMouseLeave={onPreviewEnd}
      className="relative overflow-hidden text-left"
      style={{
        borderRadius: "14px",
        height: "100px",
        background: theme.colors.surface,
        border: isActive
          ? `2px solid ${theme.colors.accent}`
          : `1px solid ${theme.colors.border}`,
        boxShadow: isActive ? `0 0 16px ${theme.colors.accent}40` : "none",
        transition: "all 200ms",
      }}
    >
      {/* Mini gradient preview strip — bottom 35% */}
      <div
        className="absolute bottom-0 left-0 right-0 h-9"
        style={{
          background: `linear-gradient(135deg, ${theme.colors.gradientPrimary.join(", ")})`,
          opacity: 0.25,
        }}
      />

      {/* Accent dots */}
      <div className="flex items-center gap-1.5 absolute top-3 left-3">
        {[theme.colors.accent, theme.colors.accentSecondary, theme.colors.accentTertiary].map((c, i) => (
          <span
            key={i}
            className="rounded-full"
            style={{ width: 8, height: 8, background: c, boxShadow: `0 0 6px ${c}80` }}
          />
        ))}
      </div>

      {/* Theme name */}
      <div
        className="absolute bottom-3 left-3 text-xs font-semibold"
        style={{ color: theme.colors.textPrimary, fontFamily: theme.typography.fontBody }}
      >
        {theme.name}
      </div>

      <div
        className="absolute bottom-3 right-3 text-[9px]"
        style={{ color: theme.colors.textMuted }}
      >
        {theme.tagline}
      </div>

      {/* Active checkmark */}
      <AnimatePresence>
        {isActive && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="absolute top-2.5 right-2.5 w-6 h-6 rounded-full flex items-center justify-center z-10"
            style={{ background: theme.colors.accent }}
          >
            <Check className="w-3 h-3 text-white" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}

// The full sheet
export function ThemeSwitcherSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { themeId, setTheme, theme: currentTheme } = useThemeStore();
  const [previewId, setPreviewId] = useState<ThemeId | null>(null);
  const displayTheme = previewId
    ? THEMES.find(t => t.id === previewId)!
    : currentTheme;

  const handleSelect = (id: ThemeId) => {
    setTheme(id);
    setPreviewId(null);
    setTimeout(onClose, 300);
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100]"
            style={{ background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)" }}
            onClick={onClose}
          />

          {/* Sheet */}
          <motion.div
            initial={{ y: "100%", x: "-50%", opacity: 0 }}
            animate={{ y: 0,      x: "-50%", opacity: 1 }}
            exit={{ y: "100%",    x: "-50%", opacity: 0 }}
            transition={{ type: "spring", stiffness: 380, damping: 35 }}
            className="fixed bottom-0 left-1/2 z-[1001] w-[calc(100%-32px)] max-w-lg"
            style={{
              background: displayTheme.colors.surface,
              borderTop: `1px solid ${displayTheme.colors.border}`,
              borderLeft:`1px solid ${displayTheme.colors.border}`,
              borderRight:`1px solid ${displayTheme.colors.border}`,
              borderRadius: "32px 32px 0 0",
              padding: "24px",
              paddingBottom: "48px",
              boxShadow: "0 -20px 40px rgba(0,0,0,0.5)",
              transition: "background 300ms, border-color 300ms",
            }}
          >
            {/* Handle */}
            <div
              className="w-10 h-1 rounded-full mx-auto mb-5"
              style={{ background: displayTheme.colors.border }}
            />

            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2
                  className="font-bold text-lg"
                  style={{
                    color: displayTheme.colors.textPrimary,
                    fontFamily: displayTheme.typography.fontDisplay,
                  }}
                >
                  Choose Theme
                </h2>
                <p
                  className="text-xs mt-0.5"
                  style={{ color: displayTheme.colors.textMuted }}
                >
                  Hover to preview · Click to apply
                </p>
              </div>
              <button 
                onClick={onClose}
                className="w-8 h-8 rounded-full flex items-center justify-center hover:opacity-80 transition-opacity"
                style={{
                  background: displayTheme.colors.surfaceAlt,
                  color: displayTheme.colors.textSecondary,
                }}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Theme grid */}
            <div className="grid grid-cols-3 gap-3">
              {THEMES.map((t) => (
                <ThemePreviewCard
                  key={t.id}
                  theme={t}
                  isActive={themeId === t.id && !previewId}
                  onSelect={() => handleSelect(t.id as ThemeId)}
                  onPreview={() => setPreviewId(t.id as ThemeId)}
                  onPreviewEnd={() => setPreviewId(null)}
                />
              ))}
            </div>

            {/* Preview label */}
            {previewId && (
              <motion.div
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 text-center text-xs"
                style={{ color: displayTheme.colors.textMuted }}
              >
                Previewing: <strong style={{ color: displayTheme.colors.accent }}>
                  {displayTheme.name}
                </strong> — release to revert
              </motion.div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

// The trigger button — shown in nav
export function ThemeTrigger() {
  const [open, setOpen] = useState(false);
  const theme = useThemeStore(s => s.theme);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full transition-all hover:scale-105"
        style={{
          background: "var(--c-accent-soft)",
          border: "1px solid var(--c-border)",
          color: "var(--c-accent)",
        }}
        title="Switch Theme"
      >
        <Palette className="w-3.5 h-3.5" />
        <span className="text-[11px] font-medium hidden sm:block">{theme.name}</span>
      </button>

      <ThemeSwitcherSheet open={open} onClose={() => setOpen(false)} />
    </>
  );
}
