"use client";

import GlassCard from "@/components/ui/GlassCard";
import AnimatedCounter from "@/components/ui/AnimatedCounter";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Props {
  label: string;
  value: number;
  suffix?: string;
  prefix?: string;
  change?: number; // percent change
  icon?: React.ReactNode;
  gradient?: string;
  delay?: number;
  decimals?: number;
}

export default function StatsCard({
  label, value, suffix, prefix, change = 0, icon, gradient, delay = 0, decimals = 0,
}: Props) {
  const TrendIcon = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Minus;
  const trendColor = change > 0 ? "text-emerald-400" : change < 0 ? "text-red-400" : "text-white/30";

  return (
    <GlassCard delay={delay} glow tilt className="p-6 group cursor-default">
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-white/80 border border-white/5"
          style={{ background: gradient || "rgba(123,47,255,0.1)" }}
        >
          {icon}
        </div>
        <div className={`flex items-center gap-1 text-[10px] font-black uppercase tracking-widest ${trendColor}`}>
          <TrendIcon className="w-3.5 h-3.5" />
          <span>{Math.abs(change)}%</span>
        </div>
      </div>
      
      <div className="text-3xl font-black text-white mb-1 tracking-tighter tabular-nums">
        <AnimatedCounter end={value} prefix={prefix} suffix={suffix} decimals={decimals} />
      </div>
      
      <div className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20">
        {label}
      </div>

      {/* Dynamic Hover Indicator */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        initial={{ width: 0, opacity: 0 }}
        whileHover={{ width: "100%", opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      />
    </GlassCard>
  );
}
