"use client";
import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  icon: LucideIcon;
  iconColor?: string;
  label: string;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

export default function PageHeader({
  icon: Icon, iconColor = "#7B2FFF", label, title, subtitle, action, className,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={cn("flex items-start justify-between mb-10 gap-4", className)}
    >
      <div>
        <div
          className="flex items-center gap-1.5 text-[10px] uppercase tracking-[0.15em] font-medium mb-3"
          style={{ color: iconColor }}
        >
          <Icon className="w-3 h-3" />
          {label}
        </div>
        <h1
          className="text-white font-bold tracking-tight mb-2"
          style={{ fontSize: "clamp(24px, 4vw, 36px)", letterSpacing: "-0.03em" }}
        >
          {title}
        </h1>
        {subtitle && (
          <p className="text-white/30 text-sm max-w-md leading-relaxed">{subtitle}</p>
        )}
      </div>
      {action && <div className="flex-shrink-0 pt-1">{action}</div>}
    </motion.div>
  );
}
