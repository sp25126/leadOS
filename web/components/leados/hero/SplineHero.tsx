"use client";
import { Suspense, useRef, useState, useCallback } from "react";
import { Canvas } from "@react-three/fiber";
import { AdaptiveDpr, AdaptiveEvents } from "@react-three/drei";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { ThemedParticles, ThemedCore, ThemedRings } from "./LeadOSScene";
import { useThemeStore } from "@/lib/themes/theme-store";
import { TypeAnimation } from "react-type-animation";
import { Search, ArrowDown, Sparkles } from "lucide-react";
import Link from "next/link";
import ActionButton from "@/components/ui/ActionButton";
import { useMediaQuery } from "@/hooks/useMediaQuery";

// Hint chip (top of hero)
function HintChip() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8, duration: 0.6 }}
      className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-8"
      style={{
        background: "rgba(123,47,255,0.08)",
        border: "1px solid rgba(123,47,255,0.2)",
        color: "rgba(167,139,250,0.9)",
      }}
    >
      <motion.span
        className="w-1.5 h-1.5 rounded-full bg-violet-400"
        animate={{ opacity: [0.4, 1, 0.4], scale: [0.8, 1.2, 0.8] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <Sparkles className="w-3 h-3" />
      AI-Powered Lead Intelligence · 5-Stage Pipeline
    </motion.div>
  );
}

// Scroll hint at bottom
function ScrollHint() {
  return (
    <motion.div
      className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 2.5, duration: 1 }}
    >
      <span className="text-[10px] uppercase tracking-[0.2em] text-white/20">Scroll</span>
      <motion.div
        className="w-px h-10 bg-gradient-to-b from-white/20 to-transparent"
        animate={{ scaleY: [0, 1, 0.5], opacity: [0, 1, 0.2] }}
        transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
      />
    </motion.div>
  );
}

// Drag hint (like spline.design)
function DragHint() {
  return (
    <motion.div
      className="absolute bottom-10 right-8 hidden lg:flex items-center gap-2 text-[11px] text-white/20"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 3, duration: 1 }}
    >
      <div className="flex gap-1">
        {[...Array(4)].map((_, i) => (
          <motion.div key={i} className="w-1 h-1 rounded-full bg-white/20"
            animate={{ opacity: [0.2, 0.8, 0.2] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>
      Drag to interact
    </motion.div>
  );
}

export default function SplineHero() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseX = useRef(0);
  const mouseY = useRef(0);
  const isDesktop = useMediaQuery("(min-width: 768px)");

  // Spring-based mouse tracking for hero tilt
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const springX = useSpring(rawX, { stiffness: 60, damping: 20 });
  const springY = useSpring(rawY, { stiffness: 60, damping: 20 });
  const rotateX = useTransform(springY, [-0.5, 0.5], [3, -3]);
  const rotateY = useTransform(springX, [-0.5, 0.5], [-5, 5]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const nx = (e.clientX - rect.left) / rect.width - 0.5;
    const ny = (e.clientY - rect.top) / rect.height - 0.5;
    rawX.set(nx);
    rawY.set(ny);
    mouseX.current = nx;
    mouseY.current = ny;
  }, [rawX, rawY]);

  const handleMouseLeave = useCallback(() => {
    rawX.set(0);
    rawY.set(0);
    mouseX.current = 0;
    mouseY.current = 0;
  }, [rawX, rawY]);

  const theme = useThemeStore(s => s.theme);
  const isCyber = theme.id === "cyber";
  const isNord  = theme.id === "nord";

  const vignetteStyle = {
    cosmic: "radial-gradient(ellipse 70% 65% at 50% 50%, transparent 30%, rgba(0,0,0,0.7) 70%, #000 100%)",
    nord:   "radial-gradient(ellipse 80% 70% at 50% 50%, transparent 40%, rgba(26,29,35,0.6) 75%, #1A1D23 100%)",
    cyber:  "linear-gradient(to bottom, rgba(2,11,4,0) 60%, rgba(2,11,4,0.8) 90%, #020B04 100%)",
  }[theme.id];

  return (
    <section
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative w-full overflow-hidden flex items-center justify-center"
      style={{ height: "100svh", minHeight: "640px" }}
    >
      {/* ── 3D Canvas (fills entire hero) ── */}
      <div className="absolute inset-0 z-0">
        {isDesktop ? (
          <Canvas
            camera={{ position: [0, 0, 8], fov: 55 }}
            dpr={[1, 1.5]}
            gl={{ antialias: false, alpha: true, powerPreference: "high-performance" }}
            style={{ background: "transparent" }}
          >
            <AdaptiveDpr pixelated />
            <AdaptiveEvents />
            <Suspense fallback={null}>
              <ThemedParticles mouseX={mouseX} mouseY={mouseY} />
              <ThemedCore />
              <ThemedRings />
            </Suspense>
          </Canvas>
        ) : (
          <div className="absolute inset-0" style={{
            background: `radial-gradient(ellipse 100% 80% at 60% 40%, ${theme.colors.accentSoft}, transparent)`
          }} />
        )}
      </div>

      {/* ── Radial vignette — centers attention ── */}
      <div className="absolute inset-0 z-[1] pointer-events-none"
        style={{
          background: vignetteStyle,
        }}
      />
      {/* Bottom fade to next section */}
      <div className="absolute bottom-0 left-0 right-0 h-48 z-[2] pointer-events-none"
        style={{ background: `linear-gradient(to bottom, transparent, ${theme.colors.background})` }}
      />

      {/* ── Centered content ── */}
      <motion.div
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className="relative z-[10] flex flex-col items-center text-center px-6 max-w-5xl mx-auto"
      >
        <HintChip />

        {/* Display headline */}
        <motion.h1
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="font-bold text-white tracking-tight mb-4 leading-[0.95]"
          style={{
            fontSize:      "clamp(48px, 8vw, 96px)",
            letterSpacing: theme.typography.trackingHero,
            fontFamily:    theme.typography.fontDisplay,
            fontWeight:    theme.typography.weightDisplay,
            color:         theme.colors.textPrimary,
            lineHeight:    isCyber ? "1.1" : "0.95",
          }}
        >
          {isCyber ? (
            // CyberTerminal: split into lines with typing animation
            <>
              <span style={{ color: theme.colors.accent }}>{">"}</span>{" "}
              <TypeAnimation
                sequence={[
                  "SCANNING_TARGETS...",
                  800,
                  "ENRICHING_LEADS...",
                  800,
                  "SCORING_PROSPECTS...",
                  800,
                  "HUNT.ENRICH.CONVERT.",
                  3000,
                ]}
                wrapper="span"
                speed={45}
                repeat={Infinity}
                style={{ color: theme.colors.accent }}
              />
            </>
          ) : isNord ? (
            // Nord Ice: clean, no special effects
            <>
              Hunt.{" "}
              <span style={{
                background: `linear-gradient(135deg, ${theme.colors.accent}, ${theme.colors.accentSecondary})`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>
                Enrich.
              </span>
              {" "}Convert.
            </>
          ) : (
            // Cosmic: existing gradient text
            <>
              Hunt.{" "}
              <span
                className="text-transparent bg-clip-text"
                style={{ backgroundImage: `linear-gradient(135deg, ${theme.colors.gradientPrimary[0]} 0%, ${theme.colors.gradientPrimary[1]} 45%, ${theme.colors.gradientPrimary[2]} 100%)` }}
              >
                Enrich.
              </span>
              {" "}Convert.
            </>
          )}
        </motion.h1>

        {/* Typewriter subtitle */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="text-white/35 mb-10 max-w-xl"
          style={{ fontSize: "clamp(14px, 2vw, 18px)", lineHeight: 1.7 }}
        >
          <TypeAnimation
            sequence={[
              800,
              "Find local businesses in any city. Enrich with phones, emails, and AI scores. Fire outreach automatically.",
              2000,
              "5-stage pipeline. Zero manual work. BYOK APIs. Production-grade lead intelligence.",
              2000,
            ]}
            wrapper="span"
            speed={65}
            repeat={Infinity}
            style={{ display: "inline-block" }}
          />
        </motion.div>

        {/* CTA row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.7 }}
          className="flex items-center gap-3 flex-wrap justify-center"
        >
          <Link href="/leados/hunt">
            <ActionButton variant="violet" className="text-sm px-7 py-3">
              <Search className="w-4 h-4" />
              Start Hunting
            </ActionButton>
          </Link>
          <Link href="#how-it-works">
            <ActionButton variant="white" className="text-sm px-7 py-3">
              See How It Works
              <ArrowDown className="w-4 h-4" />
            </ActionButton>
          </Link>
        </motion.div>

        {/* Social proof row */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8, duration: 0.8 }}
          className="flex items-center gap-6 mt-10"
        >
          {[
            { label: "Cities supported", value: "Worldwide" },
            { label: "Pipeline stages",  value: "5"         },
            { label: "Avg leads/search", value: "30–80"     },
          ].map((s, i) => (
            <div key={i} className="flex flex-col items-center">
              <span className="text-white font-semibold text-lg tracking-tight">{s.value}</span>
              <span className="text-white/25 text-[11px] mt-0.5">{s.label}</span>
            </div>
          ))}
        </motion.div>
      </motion.div>

      <ScrollHint />
      <DragHint />
    </section>
  );
}
