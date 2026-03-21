"use client";
import { useState, useRef, useEffect } from "react";
import SplineHero from "@/components/leados/hero/SplineHero";
import HowItWorks from "@/components/leados/HowItWorks";
import GlassCard from "@/components/ui/GlassCard";
import ActionButton from "@/components/ui/ActionButton";
import AnimatedCounter from "@/components/ui/AnimatedCounter";
import { motion } from "framer-motion";
import { Search, Users, Send, Activity, Zap, Mail, ArrowRight } from "lucide-react";
import Link from "next/link";
import useSWR from "swr";
import { useBYOKStore } from "@/lib/byok-store";
import { swrFetcher } from "@/lib/api";
import { useThemeStore } from "@/lib/themes/theme-store";

export default function DashboardPage() {
  const { keys } = useBYOKStore();
  const themeId = useThemeStore(s => s.theme.id);
  const isNord = themeId === "nord";
  const { data: health, error: healthErr } = useSWR(
    "/api/health", swrFetcher(keys), { refreshInterval: 10000 }
  );
  const { data: qData } = useSWR(
    "/api/leads/quota", swrFetcher(keys), { refreshInterval: 60000 }
  );
  
  const quota = qData?.stats || {};
  const isOffline = !!healthErr;

  const STATS = [
    { label: "Sessions Run",    value: quota?.total_sessions  ?? 0, icon: <Activity className="w-4 h-4" />, gradient: "rgba(123,47,255,0.15)", suffix: ""  },
    { label: "Leads Discovered",value: quota?.total_leads     ?? 0, icon: <Users className="w-4 h-4" />,    gradient: "rgba(0,229,255,0.12)",  suffix: ""  },
    { label: "READY Leads",     value: quota?.ready_leads     ?? 0, icon: <Zap className="w-4 h-4" />,      gradient: "rgba(16,185,129,0.12)", suffix: ""  },
    { label: "Emails Sent",     value: quota?.emails_sent     ?? 0, icon: <Mail className="w-4 h-4" />,     gradient: "rgba(255,45,155,0.12)", suffix: ""  },
  ];

  const videoSrc = useRef<string | null>(null);
  const [hoveredStep, setHoveredStep] = useState<number | null>(null);

  const QUICK = [
    { label: "Hunt Leads",    desc: "Search any city, any niche",   href: "/leados/hunt",     icon: Search, gradient: "from-violet-500/20 to-transparent", video: "/videos/card-float.mp4" },
    { label: "CRM Leads",     desc: "Browse enriched contacts",     href: "/leados/leads",    icon: Users,  gradient: "from-cyan-500/20 to-transparent",   video: "/videos/card-float.mp4" },
    { label: "Outreach",      desc: "Email + WhatsApp campaigns",   href: "/leados/outreach", icon: Send,   gradient: "from-pink-500/20 to-transparent",   video: "/videos/card-float.mp4" },
    { label: "Configure Keys",desc: "BYOK API key management",      href: "/leados/settings", icon: Zap,    gradient: "from-amber-500/20 to-transparent",  video: "/videos/card-float.mp4" },
  ];

  const [activeHighlight, setActiveHighlight] = useState<number | null>(0);

  useEffect(() => {
    // Cycle through stages every 3 seconds
    const interval = setInterval(() => {
      setActiveHighlight(prev => (prev === null || prev >= 4) ? 0 : prev + 1);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const PIPELINE_STAGES = [
    { n: "0", label: "Junk Filter",  icon: "🛡️", desc: "Drops 50+ junk patterns",  video: "/videos/ai-score.mp4" },
    { n: "1", label: "Google Maps",  icon: "🗺️", desc: "Phone + rating enrichment", video: "/videos/ai-score.mp4" },
    { n: "2", label: "DDG OSINT",    icon: "🔍", desc: "Email + social discovery",   video: "/videos/ai-score.mp4" },
    { n: "3", label: "Web Scrape",   icon: "🌐", desc: "Contact page extraction",    video: "/videos/ai-score.mp4" },
    { n: "4", label: "AI Scoring",   icon: "🧠", desc: "Groq/Gemini lead scoring",   video: "/videos/ai-score.mp4" },
  ];

  return (
    <div className="relative min-h-screen">

      {/* ─── Hero ─── */}
      <SplineHero />

      {/* ─── Stats ─── */}
      <section className="max-w-6xl mx-auto px-6 pb-20">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {STATS.map((s, i) => (
            <GlassCard key={s.label} delay={i * 0.1} tilt glow className="p-7">
              <div className="flex items-center gap-3 mb-6">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-white/50 border border-white/5"
                  style={{ background: s.gradient }}
                >
                  {s.icon}
                </div>
                <div className="text-[10px] font-black uppercase tracking-widest text-white/20">{s.label}</div>
              </div>
              <div className="text-4xl font-black text-white tracking-tighter tabular-nums">
                <AnimatedCounter end={s.value} suffix={s.suffix} />
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* ─── Quick Access ─── */}
      <section className="max-w-6xl mx-auto px-6 pb-20">
        <div className="flex items-center gap-4 mb-8">
            <div className="w-12 h-px bg-white/10" />
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-white/30">Module Control</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {QUICK.map((q, i) => {
            const Icon = q.icon;
            return (
              <Link key={q.label} href={q.href}>
                <GlassCard
                  delay={i * 0.1}
                  className="p-8 h-full min-h-[220px] group transition-all border-white/5 hover:border-violet-500/30"
                  glow
                  tilt
                  videoSrc={q.video}
                >
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${q.gradient} flex items-center justify-center mb-6 text-white/40 group-hover:text-white transition-all shadow-inner border border-white/5`}>
                    <Icon className="w-7 h-7" />
                  </div>
                  <div className="text-white text-lg font-black tracking-tight mb-2 uppercase">{q.label}</div>
                  <div className="text-white/30 text-xs font-medium leading-relaxed">{q.desc}</div>
                  <ArrowRight className="absolute bottom-8 right-8 w-5 h-5 text-white/10 group-hover:text-white/40 group-hover:translate-x-1 transition-all" />
                </GlassCard>
              </Link>
            );
          })}
        </div>
      </section>

      {/* ─── Pipeline Status ─── */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <GlassCard className="p-10 border-white/10 shadow-[0_0_100px_rgba(123,47,255,0.05)]">
          <div className="flex flex-col md:flex-row items-center justify-between mb-12 gap-6">
            <div>
              <h3 className="text-2xl font-black text-white uppercase tracking-tighter">Enrichment Waterfall</h3>
              <p className="text-white/30 text-sm font-medium mt-1 uppercase tracking-widest">Autonomous 5-stage reconnaissance protocol</p>
            </div>
            <div className="flex items-center gap-2 group cursor-pointer px-4 py-2 rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-[10px] font-black uppercase tracking-widest text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Operational
            </div>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {PIPELINE_STAGES.map((s, i) => (
              <motion.div
                key={s.n}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                onMouseEnter={() => setHoveredStep(i)}
                onMouseLeave={() => setHoveredStep(null)}
                className={`p-6 rounded-3xl relative overflow-hidden group hover:scale-[1.02] transition-all duration-500 border ${
                  (hoveredStep === i || activeHighlight === i)
                    ? "bg-violet-500/5 border-violet-500/30 scale-[1.02] shadow-[0_0_20px_rgba(123,47,255,0.1)]"
                    : "bg-white/[0.02] border-white/[0.05]"
                }`}
              >
                {s.video && (hoveredStep === i || activeHighlight === i) && !isNord && (
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    preload="auto"
                    className="absolute inset-0 w-full h-full object-cover opacity-40 pointer-events-none transition-opacity duration-1000"
                  >
                    <source src={s.video} type="video/mp4" />
                  </video>
                )}
                <div className="relative z-10 pointer-events-none">
                  <div className={`text-4xl mb-4 transition-all transform duration-500 ${(hoveredStep === i || activeHighlight === i) ? 'grayscale-0 scale-110' : 'grayscale group-hover:grayscale-0 group-hover:scale-110'}`}>
                    {s.icon}
                  </div>
                  <div className={`text-[9px] font-black mb-1 uppercase tracking-widest transition-colors ${(hoveredStep === i || activeHighlight === i) ? 'text-white/60' : 'text-white/20 group-hover:text-white/60'}`}>
                    Phase {s.n}
                  </div>
                  <div className="text-sm text-white font-black uppercase tracking-tight mb-2">{s.label}</div>
                  <div className={`text-[10px] font-medium leading-tight transition-colors ${(hoveredStep === i || activeHighlight === i) ? 'text-white/70' : 'text-white/30 group-hover:text-white/70'}`}>
                    {s.desc}
                  </div>
                </div>
                
                <div className="mt-6 h-1 w-full bg-white/5 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-lo-violet via-lo-cyan to-lo-violet"
                    initial={{ width: 0 }}
                    animate={{ 
                      width: "100%",
                      opacity: activeHighlight === i ? [0.4, 1, 0.4] : 1
                    }}
                    transition={{ 
                      width: { delay: i * 0.1 + 0.4, duration: 1.2 },
                      opacity: { duration: 1.5, repeat: Infinity }
                    }}
                    viewport={{ once: true }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </GlassCard>
      </section>

      {/* ─── How It Works (Scrollytelling) ─── */}
      <HowItWorks />
      
    </div>
  );
}
