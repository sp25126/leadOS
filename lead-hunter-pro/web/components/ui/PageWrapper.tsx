import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface Props {
  children: React.ReactNode;
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
}

const MAX_W = {
  sm:   "max-w-2xl",
  md:   "max-w-3xl",
  lg:   "max-w-5xl",
  xl:   "max-w-6xl",
  "2xl":"max-w-7xl",
  full: "max-w-full",
};

export default function PageWrapper({ children, className, maxWidth = "xl" }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className={cn(
        MAX_W[maxWidth],
        "mx-auto px-4 md:px-6 py-10 md:py-14 pb-28 lg:pb-14 w-full",
        className
      )}
    >
      {children}
    </motion.div>
  );
}
