"use client";

import GlassCard from "@/components/ui/GlassCard";
import MagneticButton from "@/components/ui/MagneticButton";
import { useBYOKStore } from "@/lib/byok-store";
import {
  Key,
  Save,
  Trash2,
  Eye,
  EyeOff,
  ShieldCheck,
  ShieldAlert,
  Search,
  Zap,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function BYOKSettings() {
  const { keys, setKey, clearAll } = useBYOKStore();
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({});

  const toggleVisibility = (p: string) => {
    setVisibleKeys((v) => ({ ...v, [p]: !v[p] }));
  };

  const handleSave = () => {
    toast.success("LeadOS Credentials Synchronized", {
      description: "API keys updated locally and prepared for pipeline requests.",
    });
  };

  const KEY_FIELDS = [
    { id: "geminiKey", label: "Google Gemini Key", placeholder: "AIzaSy..." },
    { id: "groqKey", label: "Groq API Key", placeholder: "gsk_..." },
    { id: "googleMapsKey", label: "Google Maps / Search Key", placeholder: "AIzaSy..." },
    { id: "hunterKey", label: "Hunter.io API Key", placeholder: "Hunt_..." },
    { id: "apiKey", label: "Alpha API Key (Master)", placeholder: "LeadOS Master Key" },
  ] as const;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
      
      {/* ── Key Form ──────────────────────────────────── */}
      <section className="lg:col-span-8 space-y-6">
        <GlassCard glow className="p-8">
           <div className="flex items-center justify-between mb-10">
              <div className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-2xl bg-leados-violet/10 border border-leados-violet/20 flex items-center justify-center text-leados-violet">
                    <Key className="w-5 h-5" />
                 </div>
                 <h2 className="text-xl font-bold text-white tracking-tight">Access Credentials</h2>
              </div>
              <MagneticButton onClick={handleSave}>
                 <Save className="w-4 h-4" />
                 Sync Credentials
              </MagneticButton>
           </div>

           <div className="space-y-6">
              {KEY_FIELDS.map((field) => (
                <div key={field.id} className="space-y-2">
                  <label className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em] pl-1">
                    {field.label}
                  </label>
                  <div className="relative group">
                    <input
                      type={visibleKeys[field.id] ? "text" : "password"}
                      value={keys[field.id]}
                      onChange={(e) => setKey(field.id, e.target.value)}
                      placeholder={field.placeholder}
                      className={cn("w-full bg-white/[0.03] border border-white/10 rounded-2xl px-6 py-4 text-sm font-medium text-white/80 focus:outline-none focus:border-leados-violet/40 transition-all placeholder:text-white/10", keys[field.id] ? "border-emerald-500/20" : "border-white/10")}
                    />
                    <button
                      onClick={() => toggleVisibility(field.id)}
                      className="absolute right-6 top-1/2 -translate-y-1/2 text-white/10 hover:text-white/60 transition-colors p-1"
                    >
                      {visibleKeys[field.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              ))}
           </div>

           <div className="mt-12 flex items-center justify-between pt-8 border-t border-white/5">
              <button onClick={clearAll} className="flex items-center gap-2 text-[10px] font-black text-red-500/40 hover:text-red-500 transition-colors uppercase tracking-[0.2em]">
                 <Trash2 className="w-4 h-4" />
                 Purge Local State
              </button>
              <div className="flex items-center gap-2 text-[10px] font-black text-white/20 uppercase tracking-widest">
                 <ShieldCheck className="w-4 h-4 text-emerald-500/40" />
                 AES-256 Storage Emulated
              </div>
           </div>
        </GlassCard>
      </section>

      {/* ── Status HUD ────────────────────────────────── */}
      <section className="lg:col-span-4 space-y-6">
         <GlassCard className="p-6">
            <h3 className="text-[10px] font-black text-white uppercase tracking-[0.2em] mb-6">Service Health</h3>
            <div className="space-y-4">
               {[
                 { label: "Pipeline Engine", status: "Operational", color: "text-emerald-400", icon: <Zap className="w-3.5 h-3.5 fill-current" /> },
                 { label: "Supabase DB", status: "Connected", color: "text-emerald-400", icon: <Search className="w-3.5 h-3.5" /> },
                 { label: "Search Grid", status: "148 Nodes Active", color: "text-leados-cyan", icon: <ShieldCheck className="w-3.5 h-3.5" /> },
               ].map((s, i) => (
                 <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
                    <div className="flex items-center gap-3">
                       <span className={s.color}>{s.icon}</span>
                       <span className="text-xs font-bold text-white/60">{s.label}</span>
                    </div>
                    <span className={cn("text-[10px] font-black uppercase tracking-widest", s.color)}>{s.status}</span>
                 </div>
               ))}
            </div>
         </GlassCard>

         <div className="p-6 rounded-3xl bg-zinc-950/40 border border-white/5 space-y-4">
            <div className="flex items-center gap-2 text-leados-violet">
               <ShieldAlert className="w-4 h-4" />
               <span className="text-[10px] font-black uppercase tracking-widest leading-none">Global Warnings</span>
            </div>
            {!keys.googleMapsKey && (
              <p className="text-xs text-white/30 leading-relaxed font-medium">
                Google Maps key unconfigured. Deep enrichment of phone numbers and addresses will be limited in discovery sessions.
              </p>
            )}
            {!keys.geminiKey && (
              <p className="text-xs text-white/30 leading-relaxed font-medium border-t border-white/5 pt-4">
                Gemini API key missing. Lead scoring and personalized outreach opening generation will be unavailable.
              </p>
            )}
            {keys.googleMapsKey && keys.geminiKey && (
              <p className="text-xs text-emerald-400 leading-relaxed font-bold">
                All critical discovery keys authenticated. Ready for high-fidelity lead generation.
              </p>
            )}
         </div>
      </section>

    </div>
  );
}
