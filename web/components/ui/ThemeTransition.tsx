"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { useThemeStore } from "@/lib/themes/theme-store";

export default function ThemeTransition() {
  const themeId = useThemeStore(s => s.themeId);
  const accent  = useThemeStore(s => s.theme.colors.accent);
  const [flash, setFlash] = useState(false);
  const [prev,  setPrev]  = useState(themeId);

  useEffect(() => {
    if (themeId !== prev) {
      setFlash(true);
      setPrev(themeId);
      setTimeout(() => setFlash(false), 400);
    }
  }, [themeId, prev]);

  return (
    <AnimatePresence>
      {flash && (
        <motion.div
          className="fixed inset-0 pointer-events-none z-[9999]"
          initial={{ opacity: 0.3 }}
          animate={{ opacity: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          style={{
            background: `radial-gradient(circle at 50% 50%, ${accent}30 0%, transparent 70%)`,
          }}
        />
      )}
    </AnimatePresence>
  );
}
