"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface Props {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  icon?: LucideIcon;
  type?: string;
  required?: boolean;
  className?: string;
  accentColor?: string;
}

export default function FloatingInput({
  label, value, onChange, placeholder, icon: Icon, type = "text",
  required, className, accentColor = "#7B2FFF",
}: Props) {
  const [focused, setFocused] = useState(false);
  const active = focused || value.length > 0;

  return (
    <div className={cn("relative", className)}>
      <motion.div
        className="absolute inset-0 rounded-xl pointer-events-none"
        animate={{
          boxShadow: focused
            ? `0 0 0 1px ${accentColor}50, 0 0 20px ${accentColor}10`
            : "0 0 0 1px transparent",
        }}
        transition={{ duration: 0.2 }}
      />

      <div
        className={cn(
          "relative flex items-center rounded-xl transition-colors duration-200",
          focused ? "bg-white/[0.04]" : "bg-white/[0.025]",
          "border",
          focused ? "border-transparent" : "border-white/[0.07]"
        )}
      >
        {Icon && (
          <div className="pl-4 pr-1 flex-shrink-0">
            <Icon
              className="w-3.5 h-3.5 transition-colors duration-200"
              style={{ color: focused ? accentColor : "rgba(255,255,255,0.25)" }}
            />
          </div>
        )}
        <div className="relative flex-1 pt-5 pb-2 px-4 h-[56px]">
          <AnimatePresence>
            <motion.label
              className="absolute left-4 pointer-events-none origin-left"
              animate={{
                top:      active ? "6px" : "50%",
                y:        active ? 0 : "-50%",
                scale:    active ? 0.72 : 1,
                color:    active ? accentColor : "rgba(255,255,255,0.25)",
              }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              style={{ fontSize: "12px", marginLeft: Icon ? "24px" : 0 }}
            >
              {label}{required && " *"}
            </motion.label>
          </AnimatePresence>
          <input
            type={type}
            value={value}
            onChange={e => onChange(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder={focused ? placeholder : ""}
            className="w-full bg-transparent text-white text-sm outline-none mt-1 placeholder-white/20"
          />
        </div>
      </div>
    </div>
  );
}
