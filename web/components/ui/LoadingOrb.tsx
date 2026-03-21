"use client";

import { motion } from "framer-motion";
import { Zap, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  label?: string;
  className?: string;
}

export default function LoadingOrb({ label, className }: Props) {
  return (
    <div className={cn("flex flex-col items-center justify-center space-y-6 py-12", className)}>
      <div className="relative">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          className="w-24 h-24 rounded-full border-2 border-dashed border-indigo-500/20"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 shadow-[0_0_20px_rgba(99,102,241,0.2)]">
            <Zap className="w-5 h-5 text-indigo-400 fill-indigo-400/20 animate-pulse" />
          </div>
        </div>
        
        {/* Orbital particles */}
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          className="absolute inset-[-10px] pointer-events-none"
        >
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
        </motion.div>
      </div>
      
      {label && (
        <div className="space-y-2 text-center">
          <h3 className="text-sm font-black uppercase tracking-widest text-white/60">{label}</h3>
          <div className="flex items-center justify-center gap-2">
            <Loader2 className="w-3 h-3 text-indigo-400 animate-spin" />
            <span className="text-[10px] font-bold text-white/20 uppercase tracking-tighter">Synchronizing Cluster</span>
          </div>
        </div>
      )}
    </div>
  );
}
