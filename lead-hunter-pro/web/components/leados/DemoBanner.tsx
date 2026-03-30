"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, X, Github, MessageCircle, Mail } from "lucide-react";
import Link from "next/link";

interface Props { onVisibilityChange?: (v: boolean) => void; }

export default function DemoBanner({ onVisibilityChange }: Props) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const dismissed = sessionStorage.getItem("leados-demo-banner");
    const v = !dismissed;
    setVisible(v);
    onVisibilityChange?.(v);
  }, []);

  const dismiss = () => {
    sessionStorage.setItem("leados-demo-banner", "1");
    setVisible(false);
    onVisibilityChange?.(false);
  };

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="fixed top-0 left-0 right-0 z-[70] overflow-hidden"
          style={{ willChange: "height" }}
        >
          <div
            className="relative flex items-center justify-center gap-3 px-4 py-2.5 text-xs flex-wrap"
            style={{
              background: "linear-gradient(90deg, rgba(123,47,255,0.12), rgba(0,229,255,0.06), rgba(255,45,155,0.10))",
              borderBottom: "1px solid rgba(255,255,255,0.05)",
            }}
          >
            {/* Top shimmer line */}
            <motion.div
              className="absolute top-0 left-0 right-0 h-px"
              style={{ background: "linear-gradient(90deg, transparent 0%, #7B2FFF 25%, #00E5FF 50%, #FF2D9B 75%, transparent 100%)" }}
              animate={{ backgroundPosition: ["0% 0%", "200% 0%"] }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            />

            <span className="text-amber-300/70 flex items-center gap-1.5">
              <AlertTriangle className="w-3 h-3 flex-shrink-0" />
              <strong className="font-medium">Demo only</strong> — not fully production grade.
            </span>
            <span className="text-white/25 hidden sm:block">·</span>
            <span className="text-white/40 hidden sm:block">Want something custom-built?</span>

            <div className="flex items-center gap-2">
              {[
                { href: "mailto:saumyavishwam@gmail.com", icon: Mail, label: "Email", color: "text-white/50" },
                { href: "https://github.com/sp25126", icon: Github, label: "GitHub", color: "text-white/50" },
                { href: "https://wa.me/918866553976", icon: MessageCircle, label: "WhatsApp", color: "text-emerald-400/70" },
              ].map(({ href, icon: Icon, label, color }) => (
                <a key={label} href={href} target="_blank"
                  className={`flex items-center gap-1 px-2 py-0.5 rounded-full border border-white/[0.06] ${color} hover:border-white/20 hover:text-white transition-all text-[11px]`}
                >
                  <Icon className="w-2.5 h-2.5" />{label}
                </a>
              ))}
              <Link href="/leados/contact"
                className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-violet-500/15 border border-violet-500/25 text-violet-300 text-[11px] hover:bg-violet-500/25 transition-all"
              >
                Hire Me →
              </Link>
            </div>

            <button onClick={dismiss}
              className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full flex items-center justify-center text-white/20 hover:text-white/60 hover:bg-white/[0.05] transition-all"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
