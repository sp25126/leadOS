"use client";
import { motion } from "framer-motion";

interface Props {
  size?: "sm" | "md" | "lg";
  label?: string;
}

const SIZES = {
  sm: { orb: 48,  ring1: 64,  ring2: 80,  ring3: 96  },
  md: { orb: 80,  ring1: 110, ring2: 140, ring3: 170 },
  lg: { orb: 120, ring1: 160, ring2: 200, ring3: 240 },
};

export default function LeadOSLoader({ size = "md", label }: Props) {
  const s = SIZES[size];

  return (
    <div className="flex flex-col items-center justify-center gap-6 py-12">
      <div
        className="relative flex items-center justify-center"
        style={{ width: s.ring3, height: s.ring3 }}
      >
        {/* Outermost ring — slowest rotation, faintest */}
        <motion.div
          className="absolute rounded-full"
          style={{
            width: s.ring3,
            height: s.ring3,
            background:
              "conic-gradient(from 0deg, transparent 0%, rgba(123,47,255,0.1) 40%, rgba(255,45,155,0.1) 70%, transparent 100%)",
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        />

        {/* Middle ring — medium rotation */}
        <motion.div
          className="absolute rounded-full shadow-[inset_0_0_20px_rgba(0,229,255,0.1)]"
          style={{
            width: s.ring2,
            height: s.ring2,
            background:
              "conic-gradient(from 180deg, transparent 0%, rgba(0,229,255,0.15) 35%, rgba(123,47,255,0.2) 65%, transparent 100%)",
          }}
          animate={{ rotate: -360 }}
          transition={{ duration: 7, repeat: Infinity, ease: "linear" }}
        />

        {/* Inner ring — fastest rotation, brightest */}
        <motion.div
          className="absolute rounded-full"
          style={{
            width: s.ring1,
            height: s.ring1,
            background:
              "conic-gradient(from 90deg, transparent 0%, rgba(255,45,155,0.3) 30%, rgba(123,47,255,0.4) 60%, rgba(0,229,255,0.2) 80%, transparent 100%)",
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
        />

        {/* Core orb — pulsating sphere */}
        <motion.div
          className="relative rounded-full z-10"
          style={{
            width: s.orb,
            height: s.orb,
            background:
              "radial-gradient(circle at 35% 35%, rgba(255,45,155,0.85) 0%, rgba(123,47,255,0.7) 40%, rgba(20,0,60,0.95) 75%, #000 100%)",
            boxShadow:
              "0 0 30px rgba(123,47,255,0.5), 0 0 60px rgba(255,45,155,0.2), 0 0 100px rgba(123,47,255,0.1)",
          }}
          animate={{
            scale: [1, 1.05, 1],
            boxShadow: [
              "0 0 30px rgba(123,47,255,0.5), 0 0 60px rgba(255,45,155,0.2)",
              "0 0 45px rgba(123,47,255,0.8), 0 0 90px rgba(255,45,155,0.4), 0 0 120px rgba(0,229,255,0.2)",
              "0 0 30px rgba(123,47,255,0.5), 0 0 60px rgba(255,45,155,0.2)",
            ],
          }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
        >
          {/* Internal Glow */}
          <div className="absolute inset-0 rounded-full bg-white/5 backdrop-blur-[2px]" />
          
          {/* Specular highlight */}
          <div
            className="absolute rounded-full"
            style={{
              width: "45%",
              height: "40%",
              top: "12%",
              left: "18%",
              background:
                "radial-gradient(circle, rgba(255,255,255,0.35) 0%, transparent 100%)",
              filter: "blur(2.5px)",
            }}
          />
        </motion.div>

        {/* Particle dots orbiting */}
        {[0, 120, 240].map((deg, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full z-20"
            style={{
              width: size === "sm" ? 3 : 5,
              height: size === "sm" ? 3 : 5,
              background: i % 2 === 0 ? "#7B2FFF" : "#FF2D9B",
              top: "50%",
              left: "50%",
              boxShadow: `0 0 8px ${i % 2 === 0 ? "#7B2FFF" : "#FF2D9B"}`,
              x: Math.cos((deg * Math.PI) / 180) * (s.ring2 / 2 - 4),
              y: Math.sin((deg * Math.PI) / 180) * (s.ring2 / 2 - 4),
            }}
            animate={{
               rotate: 360,
               scale: [1, 1.2, 1],
               opacity: [0.3, 0.9, 0.3],
            }}

            transition={{
              rotate: { duration: 6, repeat: Infinity, ease: "linear", delay: i * 0.2 },
              scale: { duration: 2, repeat: Infinity, ease: "easeInOut", delay: i * 0.3 },
              opacity: { duration: 2, repeat: Infinity, ease: "easeInOut", delay: i * 0.3 },
            }}
          />
        ))}
      </div>

      {label && (
        <div className="flex flex-col items-center gap-2">
          <motion.p
            className="text-white font-bold tracking-[0.2em] uppercase text-[10px]"
            animate={{ opacity: [0.3, 0.8, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {label}
          </motion.p>
          <div className="w-24 h-px bg-gradient-to-r from-transparent via-leados-violet/40 to-transparent" />
        </div>
      )}
    </div>
  );
}
