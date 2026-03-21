"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import PageWrapper from "@/components/ui/PageWrapper";
import PageHeader from "@/components/ui/PageHeader";
import GlassCard from "@/components/ui/GlassCard";
import ActionButton from "@/components/ui/ActionButton";
import LeadOSLoader from "@/components/ui/LeadOSLoader";
import FloatingInput from "@/components/ui/FloatingInput";
import StaggerList, { StaggerItem } from "@/components/ui/StaggerList";
import { useBYOKStore } from "@/lib/byok-store";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
  Search, MapPin, Ruler, Target, Sparkles, CheckCircle,
  AlertCircle, Users, ArrowRight, ChevronRight,
} from "lucide-react";
import Link from "next/link";

const BIZ_TYPES = ["cafe","restaurant","gym","salon","clinic","dental","bakery","hotel","pharmacy","lawyer","yoga studio","spa"];
const CITIES    = ["Ahmedabad","Pune","Mumbai","Delhi","Bangalore","Hyderabad","Surat","Dubai","Abu Dhabi","London"];
const STAGES    = [
  { icon:"🛡️", label:"Junk Filter",   detail:"Removing chains, canteens, garbage entries"   },
  { icon:"🗺️", label:"Google Maps",   detail:"Fetching phones, ratings, business hours"      },
  { icon:"🔍", label:"DDG OSINT",      detail:"Email and social media discovery"              },
  { icon:"🌐", label:"Website Scrape", detail:"Extracting contact info from business sites"  },
  { icon:"🧠", label:"AI Scoring",     detail:"Scoring leads 1-10 with personalised hooks"   },
  { icon:"💾", label:"Saving",         detail:"Writing enriched leads to database"            },
];

export default function HuntPage() {
  const { keys } = useBYOKStore();
  const [form, setForm] = useState({ business_type:"", location:"", radius_km:5, target_service:"" });
  const [loading, setLoading] = useState(false);
  const [stage,   setStage]   = useState(-1);
  const [result,  setResult]  = useState<any>(null);

  const go = async () => {
    if (!form.business_type || !form.location) {
      toast.error("Business type and location are required");
      return;
    }
    setLoading(true);
    setResult(null);
    setStage(0);

    // Animate stages non-blocking
    (async () => {
      for (let i = 0; i < STAGES.length; i++) {
        setStage(i);
        await new Promise(r => setTimeout(r, 950));
      }
    })();

    try {
      const data = await api.post("/api/leads/search", {
        business_type: form.business_type,
        location: form.location,
        radius_km: form.radius_km,
        target_service: form.target_service || "digital marketing and website development",
      }, keys);
      setResult(data);
      toast.success(`🎯 ${data.stats?.ready ?? 0} leads are outreach-ready!`);
    } catch (e: any) {
      toast.error(e.message || "Backend offline — check localhost:8000");
    } finally {
      setLoading(false);
      setStage(-1);
    }
  };

  return (
    <PageWrapper maxWidth="md">
      <PageHeader
        icon={Search}
        label="Lead Hunt"
        iconColor="#7B2FFF"
        title="Find your next clients"
        subtitle="Type a business category and city. The pipeline does the rest — automatically."
      />

      {/* Form card */}
      <GlassCard variant="elevated" className="p-6 md:p-8 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          <div>
            <FloatingInput
              label="Business Type"
              value={form.business_type}
              onChange={v => setForm({...form, business_type: v})}
              placeholder="cafe, gym, dental..."
              icon={Target}
              required
              accentColor="#7B2FFF"
            />
            <div className="flex flex-wrap gap-1.5 mt-3">
              {BIZ_TYPES.slice(0, 6).map(t => (
                <button key={t} onClick={() => setForm({...form, business_type: t})}
                  className={`text-[11px] px-2.5 py-1 rounded-full border transition-all duration-150 ${
                    form.business_type === t
                      ? "bg-violet-500/20 border-violet-500/40 text-violet-300"
                      : "border-white/[0.06] text-white/30 hover:border-white/15 hover:text-white/60"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <FloatingInput
              label="City / Location"
              value={form.location}
              onChange={v => setForm({...form, location: v})}
              placeholder="Ahmedabad, Dubai, Pune..."
              icon={MapPin}
              required
              accentColor="#00E5FF"
            />
            <div className="flex flex-wrap gap-1.5 mt-3">
              {CITIES.slice(0, 6).map(c => (
                <button key={c} onClick={() => setForm({...form, location: c})}
                  className={`text-[11px] px-2.5 py-1 rounded-full border transition-all duration-150 ${
                    form.location === c
                      ? "bg-cyan-500/20 border-cyan-500/40 text-cyan-300"
                      : "border-white/[0.06] text-white/30 hover:border-white/15 hover:text-white/60"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] text-white/30 flex items-center gap-1.5">
                <Ruler className="w-3 h-3" /> Search Radius
              </span>
              <span
                className="text-[11px] font-medium px-2 py-0.5 rounded-full"
                style={{ background: "rgba(123,47,255,0.12)", color: "#a78bfa" }}
              >
                {form.radius_km} km
              </span>
            </div>
            <input
              type="range" min={1} max={25} value={form.radius_km}
              onChange={e => setForm({...form, radius_km: +e.target.value})}
              className="w-full h-1 rounded-full appearance-none cursor-pointer"
              style={{ accentColor: "#7B2FFF" }}
            />
            <div className="flex justify-between text-[9px] text-white/15 mt-1">
              <span>1 km (local)</span><span>25 km (city-wide)</span>
            </div>
          </div>

          <div>
            <FloatingInput
              label="Target Service (for AI scoring)"
              value={form.target_service}
              onChange={v => setForm({...form, target_service: v})}
              placeholder="website design, SEO, app..."
              icon={Sparkles}
              accentColor="#FF2D9B"
            />
          </div>
        </div>

        {!keys.googleMapsKey && (
          <div
            className="flex items-start gap-2 p-3 rounded-xl mb-5 text-xs text-amber-300/70"
            style={{ background: "rgba(245,158,11,0.06)", border: "1px solid rgba(245,158,11,0.12)" }}
          >
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
            <span>No Google Maps key configured — phone coverage may be limited.{" "}
              <Link href="/leados/settings" className="text-amber-300 underline underline-offset-2">Add in Settings →</Link>
            </span>
          </div>
        )}

        <div className="flex justify-end">
          <ActionButton variant="violet" onClick={go} disabled={loading} className="px-7 py-3">
            {loading
              ? <><span className="w-4 h-4 border border-white/25 border-t-white rounded-full animate-spin mr-2" /> Hunting...</>
              : <><Search className="w-4 h-4 mr-2" /> Hunt Leads <ChevronRight className="w-4 h-4 ml-2" /></>
            }
          </ActionButton>
        </div>
      </GlassCard>

      {/* Loading state */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.4 }}
            className="mb-6"
          >
            <GlassCard variant="elevated" className="p-8">
              <div className="flex flex-col items-center mb-8">
                <LeadOSLoader size="lg" label="Pipeline active..." />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {STAGES.map((s, i) => {
                  const isDone    = stage > i;
                  const isActive  = stage === i;
                  return (
                    <motion.div
                      key={s.label}
                      className={`flex items-center gap-2.5 p-3 rounded-xl border transition-all duration-500 ${
                        isDone   ? "border-emerald-500/20 bg-emerald-500/5" :
                        isActive ? "border-violet-500/30 bg-violet-500/8" :
                                   "border-white/[0.04] bg-transparent"
                      }`}
                    >
                      <span className="text-base flex-shrink-0">{s.icon}</span>
                      <div>
                        <div className={`text-xs font-medium transition-colors ${
                          isDone ? "text-emerald-400" : isActive ? "text-white" : "text-white/25"
                        }`}>
                          {isDone ? <CheckCircle className="inline w-3 h-3 mr-1" /> : null}
                          {s.label}
                        </div>
                        {isActive && (
                          <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }}
                            className="text-[10px] text-white/30 mt-0.5 leading-tight"
                          >
                            {s.detail}
                          </motion.div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result */}
      <AnimatePresence>
        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            <GlassCard variant="glow" className="p-6 md:p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                    <span className="text-white font-semibold">Hunt Complete</span>
                  </div>
                  <p className="text-white/25 text-xs font-mono">{result.session_id}</p>
                </div>
                <div
                  className="px-3 py-1.5 rounded-full text-xs font-medium"
                  style={{ background: "rgba(16,185,129,0.12)", color: "#34d399", border: "1px solid rgba(16,185,129,0.2)" }}
                >
                  {result.stats?.ready ?? 0} ready to send
                </div>
              </div>

              <div className="grid grid-cols-5 gap-2 mb-6">
                {[
                  { l: "Discovered",    v: result.stats?.raw,          c: "text-white/60"   },
                  { l: "After Filter",  v: result.stats?.after_filter, c: "text-violet-400" },
                  { l: "With Phone",    v: result.stats?.with_phone,   c: "text-cyan-400"   },
                  { l: "With Email",    v: result.stats?.with_email,   c: "text-pink-400"   },
                  { l: "READY ✓",       v: result.stats?.ready,        c: "text-emerald-400"},
                ].map(s => (
                  <div key={s.l}
                    className="flex flex-col items-center p-3 rounded-xl text-center"
                    style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.04)" }}
                  >
                    <span className={`text-2xl font-bold tracking-tight ${s.c}`}>{s.v ?? "—"}</span>
                    <span className="text-[9px] text-white/25 mt-0.5 leading-tight">{s.l}</span>
                  </div>
                ))}
              </div>

              <div className="flex gap-3 flex-wrap">
                <Link href="/leados/leads">
                  <ActionButton variant="violet">
                    <Users className="w-4 h-4 mr-2" /> View in CRM <ArrowRight className="w-4 h-4 ml-2" />
                  </ActionButton>
                </Link>
                <ActionButton variant="white" onClick={() => setResult(null)}>
                  Hunt Again
                </ActionButton>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </PageWrapper>
  );
}
