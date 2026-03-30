"use client";

import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface Props {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  variant?: "primary" | "ghost";
}

export default function MagneticButton({
  children,
  className = "",
  onClick,
  variant = "primary",
}: Props) {
  const ref = useRef<HTMLButtonElement>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = (e.clientX - rect.left - rect.width / 2) * 0.35;
    const y = (e.clientY - rect.top - rect.height / 2) * 0.35;
    setPos({ x, y });
  };

  const base =
    variant === "primary"
      ? "relative px-6 py-3 rounded-full text-sm font-medium text-white overflow-hidden"
      : "relative px-6 py-3 rounded-full text-sm font-medium text-white/80 border border-white/10 backdrop-blur-sm hover:border-white/20 transition-colors";

  return (
    <motion.button
      ref={ref}
      animate={{ x: pos.x, y: pos.y }}
      transition={{ type: "spring", stiffness: 300, damping: 20, mass: 0.5 }}
      onMouseMove={handleMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setPos({ x: 0, y: 0 });
        setIsHovered(false);
      }}
      onClick={onClick}
      className={cn(base, className)}
    >
      {variant === "primary" && (
        <>
          <span
            className="absolute inset-0 rounded-full"
            style={{
              background:
                "linear-gradient(135deg, #7B2FFF 0%, #00E5FF 50%, #FF2D9B 100%)",
            }}
          />
          <AnimatePresence>
            {isHovered && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 rounded-full"
                style={{
                  background:
                    "linear-gradient(135deg, #00E5FF 0%, #FF2D9B 50%, #7B2FFF 100%)",
                }}
                transition={{ duration: 0.3 }}
              />
            )}
          </AnimatePresence>
        </>
      )}
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </motion.button>
  );
}
