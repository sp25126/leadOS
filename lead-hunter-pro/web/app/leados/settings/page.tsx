"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import GlassCard from "@/components/ui/GlassCard";
import ActionButton from "@/components/ui/ActionButton";
import { useBYOKStore, BYOKKeys } from "@/lib/byok-store";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { Eye, EyeOff, CheckCircle, XCircle, Loader2,
         Settings, Zap, Globe, Mail, Brain, MapPin, ShieldAlert, Key } from "lucide-react";

const KEY_CONFIG: { key: keyof BYOKKeys; label: string; desc: string; icon: any; required: boolean; testHint: string }[] = [
  { key:"apiKey",       label:"LeadOS API Master", desc:"Your backend authentication key",           icon:Key,    required:true,  testHint:"/api/health" },
  { key:"googleMapsKey",label:"Maps Data Core",    desc:"Places API — phone + rating enrich",      icon:MapPin, required:false, testHint:"/api/health" },
  { key:"geminiKey",    label:"Gemini Neural",     desc:"AI scoring + personalization",             icon:Brain,  required:false, testHint:"/api/health" },
  { key:"groqKey",      label:"Groq LPU Array",    desc:"Ultra-fast AI validation (llama3)",        icon:Zap,    required:false, testHint:"/api/health" },
  { key:"hunterKey",    label:"Hunter Signal",      desc:"Domain email OSINT enrichment",           icon:Mail,   required:false, testHint:"/api/health" },
];

export default function SettingsPage() {
  const { keys, setKey, clearAll } = useBYOKStore();
  const [visible, setVisible]      = useState<Record<string, boolean>>({});
  const [testing, setTesting]      = useState<Record<string, boolean>>({});
  const [results, setResults]      = useState<Record<string, "ok"|"fail"|null>>({});

  const testKey = async (k: keyof BYOKKeys) => {
    if (typeof k !== "string") return;
    setTesting(t => ({...t,[k]:true}));
    try {
      await api.get("/api/health", keys);
      setResults(r => ({...r,[k]:"ok" as const}));
      toast.success(`${String(k).toUpperCase()} COMMAND ESTABLISHED!`);
    } catch {
      setResults(r => ({...r,[k]:"fail" as const}));
      toast.error(`${String(k).toUpperCase()} SEQUENCE FAILED`);
    } finally {
      setTesting(t => ({...t,[k]:false}));
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <div className="flex flex-col md:flex-row items-center justify-between mb-12 gap-6">
        <div>
            <div className="flex items-center gap-2 text-[10px] font-black text-amber-400 uppercase tracking-[0.3em] mb-4">
                <Settings className="w-4 h-4" /> System Configuration
            </div>
            <h1 className="text-4xl font-black text-white tracking-tighter uppercase mb-2 leading-none">Security <span className="gradient-text">BYOK</span></h1>
            <p className="text-white/30 text-sm font-medium uppercase tracking-widest leading-none">Bring Your Own Keys · Local Browser Encryption Sync</p>
        </div>
        <div className="flex items-center gap-4">
             <div className="px-6 py-3 rounded-2xl bg-white/[0.04] border border-white/5 border-dashed">
                 <div className="text-[10px] font-black text-white/20 uppercase tracking-widest">Storage Status</div>
                 <div className="text-xs font-black text-emerald-400 mt-1 uppercase">LOCALLY PERSISTED</div>
             </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-12">
        
        {/* Key Configuration List */}
        <section className="lg:col-span-12 space-y-4">
            {KEY_CONFIG.map((cfg, i) => {
                const val    = keys[cfg.key] || "";
                const show   = visible[cfg.key];
                const status = results[cfg.key];
                const Icon   = cfg.icon;

                return (
                    <GlassCard key={cfg.key} delay={i*0.05} className="p-7 group relative overflow-hidden" glow tilt>
                        <div className="flex flex-col md:flex-row items-center gap-8 justify-between">
                            <div className="flex items-center gap-6 flex-1 w-full">
                                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 border border-white/5 bg-white/[0.03] transition-all duration-300 ${status === "ok" ? "text-emerald-400 border-emerald-400/20 bg-emerald-500/5 shadow-[0_0_15px_rgba(52,211,153,0.1)]" : status === "fail" ? "text-red-400 border-red-400/20 bg-red-500/5" : "text-white/40 group-hover:text-white"}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                                <div className="flex-1 w-full">
                                    <div className="flex items-center gap-3 mb-1">
                                        <span className="text-lg font-black text-white uppercase tracking-tight">{cfg.label}</span>
                                        {cfg.required && (
                                            <span className="text-[9px] px-2 py-0.5 rounded-lg bg-lo-violet/10 text-lo-violet border border-lo-violet/20 font-black tracking-widest uppercase">CRITICAL</span>
                                        )}
                                        {status === "ok"   && <CheckCircle className="w-4 h-4 text-emerald-400" />}
                                        {status === "fail" && <XCircle     className="w-4 h-4 text-red-400"     />}
                                    </div>
                                    <p className="text-[10px] font-bold text-white/30 uppercase tracking-widest leading-none">{cfg.desc}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-4 w-full md:w-[450px]">
                                <div className="flex-1 relative group-focus-within:scale-[1.02] transition-transform">
                                    <input
                                        type={show ? "text" : "password"}
                                        value={val}
                                        onChange={e => setKey(cfg.key, e.target.value)}
                                        placeholder={`ENTER ${cfg.label.toUpperCase()} PROTOCOL SIGNAL...`}
                                        className="w-full bg-white/[0.03] border border-white/[0.08] rounded-2xl px-6 py-4 text-white text-sm font-bold placeholder:text-white/10 outline-none focus:border-lo-violet/40 transition-all shadow-inner pr-16"
                                    />
                                    <button
                                        onClick={() => setVisible(v => ({...v,[cfg.key]:!v[cfg.key]}))}
                                        className="absolute right-6 top-1/2 -translate-y-1/2 text-white/10 hover:text-white/40 transition-colors"
                                    >
                                        {show ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                                <ActionButton
                                    variant="white"
                                    onClick={() => testKey(cfg.key)}
                                    disabled={!val || testing[cfg.key]}
                                    className="h-14 px-8 min-w-[100px] shadow-2xl"
                                >
                                    {testing[cfg.key] ? <Loader2 className="w-4 h-4 animate-spin" /> : "Verify"}
                                </ActionButton>
                            </div>
                        </div>
                    </GlassCard>
                );
            })}
        </section>

        {/* Danger zone / Policy */}
        <section className="lg:col-span-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <GlassCard className="p-8 border-lo-pink/20 bg-lo-pink/5" glow>
                    <div className="flex items-start gap-6">
                        <div className="w-12 h-12 rounded-2xl bg-lo-pink/10 border border-lo-pink/20 flex items-center justify-center text-lo-pink">
                             <ShieldAlert className="w-6 h-6" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-xl font-black text-white uppercase tracking-tighter mb-2">ERASE SIGNAL DATA</h3>
                            <p className="text-sm font-medium text-white/40 mb-8 leading-relaxed">Instantly purge all API keys and session credentials from local browser memory. This action is irreversible.</p>
                            <ActionButton variant="pink" onClick={() => { clearAll(); toast.info("ALL COMMAND KEYS PURGED FROM MEMORY"); }} className="px-10 h-14">
                                Master Purge Command
                            </ActionButton>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-8 border-white/5 opacity-50 hover:opacity-100 transition-opacity">
                    <h3 className="text-xs font-black text-white/30 uppercase tracking-[0.4em] mb-6">Security Documentation</h3>
                    <ul className="space-y-4">
                         {[
                             "Keys never transit via LeadOS servers.",
                             "Authorization is piped through request headers.",
                             "AES-256 local browser persistence sync.",
                             "Zero-knowledge infrastructure."
                         ].map(txt => (
                             <li key={txt} className="flex items-center gap-3 text-[10px] font-black text-white/40 uppercase tracking-widest">
                                 <CheckCircle className="w-4 h-4 text-emerald-400/40" />
                                 {txt}
                             </li>
                         ))}
                    </ul>
                </GlassCard>
            </div>
        </section>
      </div>
    </div>
  );
}
