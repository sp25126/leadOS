import { cn } from "@/lib/utils";

interface TextProps {
  children: React.ReactNode;
  className?: string;
}

export function DisplayText({ children, className }: TextProps) {
  return (
    <h1
      className={cn("font-bold text-white leading-none tracking-[-0.04em]", className)}
      style={{ fontSize: "clamp(48px, 8vw, 96px)" }}
    >
      {children}
    </h1>
  );
}

export function HeadingXL({ children, className }: TextProps) {
  return (
    <h1
      className={cn("font-bold text-white leading-tight tracking-[-0.03em]", className)}
      style={{ fontSize: "clamp(32px, 5vw, 64px)" }}
    >
      {children}
    </h1>
  );
}

export function HeadingLG({ children, className }: TextProps) {
  return (
    <h2
      className={cn("font-bold text-white leading-tight tracking-[-0.025em]", className)}
      style={{ fontSize: "clamp(22px, 3vw, 40px)" }}
    >
      {children}
    </h2>
  );
}

export function HeadingMD({ children, className }: TextProps) {
  return (
    <h3 className={cn("text-white font-semibold text-lg tracking-[-0.02em] leading-snug", className)}>
      {children}
    </h3>
  );
}

export function BodyLG({ children, className }: TextProps) {
  return (
    <p className={cn("text-white/50 text-base leading-relaxed", className)}>
      {children}
    </p>
  );
}

export function Body({ children, className }: TextProps) {
  return (
    <p className={cn("text-white/40 text-sm leading-relaxed", className)}>
      {children}
    </p>
  );
}

export function Label({ children, className }: TextProps) {
  return (
    <span className={cn("text-[10px] font-medium uppercase tracking-[0.12em] text-white/25", className)}>
      {children}
    </span>
  );
}

export function GradientText({ children, className }: TextProps) {
  return (
    <span
      className={cn("text-transparent bg-clip-text", className)}
      style={{ backgroundImage: "linear-gradient(135deg, #7B2FFF 0%, #00E5FF 45%, #FF2D9B 100%)" }}
    >
      {children}
    </span>
  );
}
