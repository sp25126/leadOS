"use client";
import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search, Filter, Map, Globe, Brain,
  ArrowRight, Check, Zap, ChevronDown,
} from "lucide-react";
import { useThemeStore } from "@/lib/themes/theme-store";

const STEPS = [
  {
    step: "01",
    icon: Search,
    title: "You Hunt",
    subtitle: "Pick a city. Pick a business type.",
    desc: "Type 'cafe' and 'Ahmedabad'. LeadOS fires an OpenStreetMap Overpass query across your chosen radius — pulling every matching business node, way, and relation from the global OSM database.",
    detail: "No API limits. No signup required. Just raw geographic data.",
    color: "#7B2FFF",
    code: `POST /api/leads/search
{
  "business_type": "cafe",
  "location": "Ahmedabad",
  "radius_km": 5
}`,
    visual: "orb",
  },
  {
    step: "02",
    icon: Filter,
    title: "Junk Gets Killed",
    subtitle: "Stage 0 — Automatic junk filter.",
    desc: "Before any enrichment happens, 50+ business name patterns are checked. Police canteens, hostel messes, government offices, franchise chains — all dropped instantly. Only real businesses survive.",
    detail: "McDonald's, KFC, canteen, students mess → gone.",
    color: "#FF2D9B",
    code: `[FILTER] Dropped 12/48:
- "Judicial Canteen" → junk_pattern
- "McDonald's" → chain_brand
- "waah" → garbage_osm_name
→ 36 leads proceed to enrichment`,
    visual: "filter",
  },
  {
    step: "03",
    icon: Map,
    title: "Google Maps Enriches",
    subtitle: "Stage 1 — BYOK Google Places API.",
    desc: "Each surviving lead is matched against Google Places to pull phone numbers, ratings, review counts, and business hours. You bring your own API key — your quota, your control.",
    detail: "Phone coverage jumps from ~10% to ~65% after this stage.",
    color: "#00E5FF",
    code: `[GMAPS] "Cafe Mysore" matched
  phone:   +91 98765 43210  ✓
  rating:  4.3 (127 reviews)
  hours:   Mo-Su 08:00-22:00
  status:  OPERATIONAL`,
    visual: "maps",
  },
  {
    step: "04",
    icon: Globe,
    title: "OSINT Hunts Emails",
    subtitle: "Stage 2+3 — DDG scraper + website parser.",
    desc: "DuckDuckGo search queries are fired for each business: 'Cafe Mysore Ahmedabad email contact'. Results are scraped for email patterns. Then the business website is parsed for contact pages, social handles, and tech stack hints.",
    detail: "Finds Instagram, Facebook, LinkedIn, WhatsApp links too.",
    color: "#22c55e",
    code: `[DDG] Query: "Cafe Mysore Ahmedabad email"
[SCRAPE] https://cafemysore.in/contact
  email:   hello@cafemysore.in  (score: 3)
  social:  {instagram: "cafemysore_ahm"}
  tech:    wordpress, whatsapp_widget`,
    visual: "osint",
  },
  {
    step: "05",
    icon: Brain,
    title: "AI Scores & Personalizes",
    subtitle: "Stage 4 — Groq / Gemini BYOK scoring.",
    desc: "Every lead gets an AI score from 1-10 based on their digital presence gaps. No website? Score jumps. No social? Score jumps. The AI also generates a personalized opening line for outreach — specific to their business, not a template.",
    detail: "Flat-5 scoring is dead. Real variance. Real personalization.",
    color: "#f59e0b",
    code: `Score: 8/10
Pain Points:
  - No website (losing walk-in customers)
  - Instagram not active since 6 months

Opening:
  "Hi, I was searching for cafes near
  ISCON and couldn't find Cafe Mysore
  online — you're missing..."`,
    visual: "ai",
  },
  {
    step: "06",
    icon: Zap,
    title: "Outreach Fires",
    subtitle: "Stage 5 — Email + WhatsApp automation.",
    desc: "READY leads (those with email + score ≥ 6) are queued for outreach. The engine sends personalized emails with the AI-generated opening, tracking sent/failed/remaining in real time.",
    detail: "Custom SMTP, WA gateway, or Resend API.",
    color: "#7B2FFF",
    code: `[OUTREACH] Session: cafe_ahmedabad_123
  Sending to: hello@cafemysore.in
  Subject: Quick question about Cafe Mysore
  Opening: "Hi, I was searching..."
  [SENT] ✓  Elapsed: 1.2s`,
    visual: "outreach",
  },
];

// Mini visual for each step
function StepVisual({ type, color }: { type: string; color: string }) {
  const themeId = useThemeStore(s => s.theme.id);
  const isNord = themeId === "nord";
  const base = "rounded-2xl border border-white/[0.06] bg-white/[0.02] w-full h-full flex items-center justify-center overflow-hidden";

  if (type === "orb") return (
    <div className={base}>
      <div className="relative">
        <motion.div
          className="w-32 h-32 rounded-full"
          style={{ 
            background: isNord 
              ? `radial-gradient(circle at 35% 35%, #ECEFF4cc, #D0877066, transparent)`
              : `radial-gradient(circle at 35% 35%, ${color}cc, ${color}33, transparent)`, 
            boxShadow: isNord
              ? `0 0 60px #D0877044`
              : `0 0 60px ${color}55` 
          }}
          animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }}
          transition={{ duration: 3, repeat: Infinity }}
        />
        <motion.div
          className="absolute inset-0 rounded-full border"
          style={{ borderColor: isNord ? "#D0877033" : `${color}44` }}
          animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </div>
    </div>
  );

  if (type === "filter") return (
    <div className={base}>
      <div className="space-y-2 w-full px-8">
        {["Judicial Canteen","McDonald's","waah","NMC Hospital","Starbucks","Student Mess"].map((name, i) => (
          <motion.div key={name}
            initial={{ opacity: 1, x: 0, textDecoration: "none" }}
            animate={{ opacity: [1, 0.3, 1], x: [0, 5, 0], textDecoration: ["none", "line-through", "none"] }}
            transition={{ delay: i * 0.4, duration: 2, repeat: Infinity, repeatDelay: 1 }}
            className="flex items-center gap-2 text-xs text-white/50"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
            {name}
          </motion.div>
        ))}
      </div>
    </div>
  );

  if (type === "maps") return (
    <div className={base}>
      <div className="text-center">
        <div className="grid grid-cols-3 gap-3 mb-4">
          {["📞 Phone","⭐ Rating","🕐 Hours"].map((l, i) => (
            <motion.div key={l}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.3, repeat: Infinity, repeatDelay: 2 }}
              className="px-2 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.06] text-[10px] text-white/50"
            >
              {l}
            </motion.div>
          ))}
        </div>
        <motion.div
          className="text-xs text-cyan-400"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          Enriching...
        </motion.div>
      </div>
    </div>
  );

  if (type === "osint") return (
    <div className={base}>
      <div className="space-y-1.5 w-full px-6">
        {[
          { label: "@instagram",  found: true,  color: "#E1306C" },
          { label: "email",       found: true,  color: "#22c55e" },
          { label: "@facebook",   found: false, color: "#4267B2" },
          { label: "whatsapp",    found: true,  color: "#25D366" },
          { label: "linkedin",    found: false, color: "#0A66C2" },
        ].map((item, i) => (
          <motion.div key={item.label}
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: i * 0.2, repeat: Infinity, repeatDelay: 1.5 }}
            className="flex items-center justify-between"
          >
            <span className="text-[11px] text-white/40">{item.label}</span>
            <span className={`text-[10px] ${item.found ? "text-emerald-400" : "text-white/20"}`}>
              {item.found ? "✓ found" : "— not found"}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );

  if (type === "ai") return (
    <div className={base}>
      <div className="text-center px-6">
        <motion.div
          className="text-5xl font-bold mb-2"
          style={{ color }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          8<span className="text-2xl text-white/30">/10</span>
        </motion.div>
        <div className="space-y-1">
          {["No website", "Inactive social", "High rating, low reviews"].map((p, i) => (
            <motion.div key={p}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.5, repeat: Infinity, repeatDelay: 1 }}
              className="text-[10px] text-white/40 flex items-center gap-1"
            >
              <span className="w-1 h-1 rounded-full bg-amber-400 flex-shrink-0" />{p}
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className={base}>
      <motion.div
        className="text-center"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="text-3xl mb-2">📤</div>
        <div className="text-xs text-white/30">Outreach running</div>
        <motion.div
          className="mt-3 h-1 w-32 rounded-full bg-white/[0.06] overflow-hidden mx-auto"
        >
          <motion.div
            className="h-full rounded-full"
            style={{ background: `linear-gradient(90deg, ${color}, transparent)` }}
            animate={{ width: ["0%", "100%"] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
          />
        </motion.div>
      </motion.div>
    </div>
  );
}

function PipelineVideo({ active }: { active: boolean }) {
  const isNord = useThemeStore(s => s.theme.id) === "nord";
  if (!active || isNord) return null;
  return (
    <video
      autoPlay
      loop
      muted
      playsInline
      preload="auto"
      className="absolute inset-0 w-full h-full object-cover opacity-[0.06] pointer-events-none z-0 transition-opacity duration-1000"
    >
      <source src="/videos/pipeline.mp4" type="video/mp4" />
    </video>
  );
}

export default function HowItWorks() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const [isHoveredStep, setIsHoveredStep] = useState<number | null>(null);
  const stepRefs = useRef<(HTMLDivElement | null)[]>([]);

  // IntersectionObserver-based step activation (no GSAP dep issues)
  useEffect(() => {
    const observers = stepRefs.current.map((el, i) => {
      if (!el) return null;
      const obs = new IntersectionObserver(
        ([entry]) => { if (entry.isIntersecting) setActiveStep(i); },
        { threshold: 0.5, rootMargin: "-20% 0px -20% 0px" }
      );
      obs.observe(el);
      return obs;
    });
    return () => observers.forEach(o => o?.disconnect());
  }, []);

  const step = STEPS[activeStep];
  const Icon = step.icon;

  return (
    <section className="relative bg-black overflow-hidden" id="how-it-works">
      {/* Background image asset */}
      <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
        <img 
          src="/images/howit-bg.png" 
          alt="" 
          loading="lazy"
          className="w-full h-full object-cover lg:object-contain" 
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black" />
      </div>

      {/* Section header */}
      <div className="max-w-6xl mx-auto px-6 pt-24 pb-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/[0.06] bg-white/[0.02] text-xs text-white/40 mb-4"
        >
          <Zap className="w-3 h-3 text-violet-400" />
          How LeadOS Works
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4"
        >
          From zero to{" "}
          <span
            className="text-transparent bg-clip-text"
            style={{ backgroundImage: "linear-gradient(135deg,#7B2FFF,#00E5FF,#FF2D9B)" }}
          >
            outreach-ready leads
          </span>
          <br />in under 60 seconds.
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="text-white/30 text-base max-w-xl mx-auto"
        >
          Scroll through the pipeline to see exactly what happens to your leads — stage by stage.
        </motion.p>
        <motion.div
          className="flex justify-center mt-6"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <ChevronDown className="w-5 h-5 text-white/20" />
        </motion.div>
      </div>

      {/* Sticky two-column layout */}
      <div className="relative max-w-6xl mx-auto px-6">
        <div className="flex gap-8 lg:gap-16">

          {/* LEFT: sticky visual panel */}
          <div className="hidden lg:block w-[45%] flex-shrink-0 z-10">
            <div className="sticky top-28">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeStep}
                  initial={{ opacity: 0, y: 20, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.97 }}
                  transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                  className="space-y-5 relative"
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                >
                  <PipelineVideo active={isHovered} />
                  {/* Step number */}
                  <div className="flex items-center gap-3">
                    <span
                      className="text-5xl font-bold tabular-nums"
                      style={{ color: step.color, opacity: 0.4 }}
                    >
                      {step.step}
                    </span>
                    <div
                      className="flex-1 h-px"
                      style={{ background: `linear-gradient(90deg, ${step.color}44, transparent)` }}
                    />
                  </div>

                  {/* Icon + title */}
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center"
                      style={{ background: `${step.color}18`, border: `1px solid ${step.color}30` }}
                    >
                      <Icon className="w-5 h-5" style={{ color: step.color }} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-xl">{step.title}</h3>
                      <p className="text-white/30 text-sm">{step.subtitle}</p>
                    </div>
                  </div>

                  {/* Visual animation */}
                  <div className="h-48 rounded-2xl overflow-hidden">
                    <StepVisual type={step.visual} color={step.color} />
                  </div>

                  {/* Code block */}
                  <div
                    className="rounded-xl p-4 font-mono text-[11px] leading-relaxed"
                    style={{
                      background: "rgba(255,255,255,0.02)",
                      border: "1px solid rgba(255,255,255,0.05)",
                    }}
                  >
                    <div className="flex items-center gap-1.5 mb-3">
                      {[step.color + "66", step.color + "44", step.color + "22"].map((c, i) => (
                        <span key={i} className="w-2 h-2 rounded-full" style={{ background: c }} />
                      ))}
                    </div>
                    <pre className="text-white/40 whitespace-pre-wrap">{step.code}</pre>
                  </div>

                  {/* Progress dots */}
                  <div className="flex items-center gap-2">
                    {STEPS.map((_, i) => (
                      <motion.div
                        key={i}
                        className="h-1 rounded-full transition-all duration-500"
                        style={{
                          width: i === activeStep ? 24 : 6,
                          background: i === activeStep ? step.color : "rgba(255,255,255,0.1)",
                        }}
                      />
                    ))}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          {/* RIGHT: scroll steps */}
          <div className="flex-1 space-y-0 z-20">
            {STEPS.map((s, i) => {
              const SIcon = s.icon;
              const isActive = activeStep === i;
              return (
                <div
                  key={s.step}
                  ref={el => { stepRefs.current[i] = el; }}
                  className="min-h-[70vh] flex items-center py-16"
                >
                  <motion.div
                    className={`
                      w-full p-6 rounded-2xl border transition-all duration-500
                      ${isActive
                        ? "border-white/[0.1] bg-white/[0.03]"
                        : "border-white/[0.03] bg-transparent"
                      }
                    `}
                    onMouseEnter={() => setIsHoveredStep(i)}
                    onMouseLeave={() => setIsHoveredStep(null)}
                  >
                    <PipelineVideo active={isHoveredStep === i || (isActive && typeof window !== 'undefined' && window.innerWidth < 1024)} />
                    {/* Mobile: show visual too */}
                    <div className="lg:hidden mb-5 h-40 rounded-xl overflow-hidden">
                      <StepVisual type={s.visual} color={s.color} />
                    </div>

                    <div className="flex items-start gap-4">
                      <div
                        className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-500 ${
                          isActive ? "scale-110" : "scale-100 opacity-40"
                        }`}
                        style={{
                          background: isActive ? `${s.color}20` : "rgba(255,255,255,0.03)",
                          border: `1px solid ${isActive ? s.color + "40" : "rgba(255,255,255,0.05)"}`,
                        }}
                      >
                        <SIcon className="w-5 h-5" style={{ color: isActive ? s.color : "rgba(255,255,255,0.3)" }} />
                      </div>
                      <div>
                        <span
                          className="text-[10px] font-bold uppercase tracking-widest mb-1 block"
                          style={{ color: isActive ? s.color : "rgba(255,255,255,0.2)" }}
                        >
                          Stage {s.step}
                        </span>
                        <h3
                          className={`text-xl font-bold mb-1 transition-colors ${isActive ? "text-white" : "text-white/30"}`}
                        >
                          {s.title}
                        </h3>
                        <p className={`text-sm mb-3 transition-colors ${isActive ? "text-white/40" : "text-white/15"}`}>
                          {s.subtitle}
                        </p>
                        <AnimatePresence>
                          {isActive && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.3 }}
                            >
                              <p className="text-white/50 text-sm leading-relaxed mb-3">{s.desc}</p>
                              <div
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs"
                                style={{
                                  background: `${s.color}10`,
                                  border: `1px solid ${s.color}25`,
                                  color: s.color,
                                }}
                              >
                                <Check className="w-3 h-3" />{s.detail}
                              </div>

                              {/* Mobile code block */}
                              <div
                                className="lg:hidden mt-4 rounded-xl p-3 font-mono text-[10px] leading-relaxed"
                                style={{
                                  background: "rgba(255,255,255,0.02)",
                                  border: "1px solid rgba(255,255,255,0.04)",
                                }}
                              >
                                <pre className="text-white/30 whitespace-pre-wrap overflow-x-auto">{s.code}</pre>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </motion.div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
