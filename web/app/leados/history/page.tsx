"use client";
import { motion, AnimatePresence } from "framer-motion";
import GlassCard from "@/components/ui/GlassCard";
import ActionButton from "@/components/ui/ActionButton";
import LeadOSLoader from "@/components/ui/LeadOSLoader";
import { useBYOKStore } from "@/lib/byok-store";
import { swrFetcher, api } from "@/lib/api";
import useSWR from "swr";
import { toast } from "sonner";
import { History, Users, CheckCircle, Trash2, ArrowRight, Calendar, Activity, Zap, ShieldCheck } from "lucide-react";
import Link from "next/link";

export default function HistoryPage() {
  const { keys } = useBYOKStore();
  const { data, isLoading, mutate } = useSWR("/api/leads/history", swrFetcher(keys), { refreshInterval: 60000 });
  const sessions = [...(data?.sessions ?? [])].sort(
    (a:any,b:any) => (b.created_at ?? 0) - (a.created_at ?? 0)
  );

  const deleteSession = async (id: string) => {
    try {
      await api.delete(`/api/leads/history/${id}`, keys);
      toast.success("SESSION PERMANENTLY ERASED");
      mutate();
    } catch(e:any) { toast.error(e.message || "Deletion Failed"); }
  };

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      <LeadOSLoader size="lg" label="Retrieving Historical Intelligence..." />
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="flex flex-col md:flex-row items-center justify-between mb-12 gap-6">
        <div>
            <div className="flex items-center gap-2 text-[10px] font-black text-lo-cyan uppercase tracking-[0.3em] mb-4">
                <History className="w-4 h-4" /> RECONNAISSANCE ARCHIVE
            </div>
            <h1 className="text-4xl font-black text-white tracking-tighter uppercase mb-2 leading-none">Extraction <span className="gradient-text">History</span></h1>
            <p className="text-white/30 text-sm font-medium uppercase tracking-widest">{sessions.length} Logged Recon Missions · Central Ops Sync Archive</p>
        </div>
        <div className="flex items-center gap-4">
            <div className="px-5 py-3 rounded-2xl border border-white/5 bg-white/[0.02] text-center">
                 <div className="text-2xl font-black text-white tabular-nums tracking-tighter">{sessions.length}</div>
                 <div className="text-[9px] font-black text-white/20 uppercase tracking-widest">Saved Missions</div>
            </div>
        </div>
      </div>

      <AnimatePresence mode="popLayout">
        {sessions.length === 0 ? (
          <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }}>
            <GlassCard className="p-24 text-center border-white/5">
                <ShieldCheck className="w-12 h-12 text-white/5 mx-auto mb-6" />
                <h3 className="text-xl font-black text-white/20 uppercase tracking-tighter mb-4">No Historical Records Found</h3>
                <Link href="/leados/hunt">
                    <ActionButton variant="violet" className="mx-auto h-12 px-8">Initialize Command Alpha</ActionButton>
                </Link>
            </GlassCard>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sessions.map((s:any, i:number) => (
              <motion.div 
                key={s.session_id} 
                initial={{ opacity:0, y:20 }} 
                animate={{ opacity:1, y:0 }} 
                exit={{ opacity:0, x:-20 }}
                transition={{ delay: i * 0.05, duration: 0.5 }}
              >
                <GlassCard tilt glow className="p-7 border-white/5 hover:border-lo-cyan/30 transition-all group relative overflow-hidden h-full">
                    {/* Background glow node */}
                    <div className="absolute -top-10 -right-10 w-32 h-32 bg-lo-cyan/5 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                    
                    <div className="flex items-start justify-between mb-8">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-2xl flex items-center justify-center border border-white/5 bg-white/[0.03] text-white/40 group-hover:bg-lo-cyan/10 group-hover:text-lo-cyan group-hover:border-lo-cyan/20 transition-all">
                                <Activity className="w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="text-lg font-black text-white tracking-tighter uppercase leading-none mb-1.5">{s.business_type || "Niche Extraction"}</h3>
                                <div className="flex items-center gap-2 text-[10px] font-black text-white/20 uppercase tracking-widest">
                                    <Calendar className="w-3 h-3" />
                                    {s.created_at ? new Date(s.created_at * 1000).toLocaleDateString() : "STAMP UNKNOWN"}
                                    <span className="w-1 h-1 rounded-full bg-white/10" />
                                    {s.location || "GLOBAL GRID"}
                                </div>
                            </div>
                        </div>
                        <div className="p-2 rounded-lg bg-white/[0.03] text-[9px] font-black tracking-widest uppercase text-white/20 group-hover:text-lo-cyan transition-colors">
                            ID_{s.session_id.slice(-6)}
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-10">
                        <div className="p-4 rounded-2xl bg-white/[0.01] border border-white/[0.03]">
                             <div className="text-xl font-black text-white tabular-nums tracking-tighter">{s.total_count ?? "?"}</div>
                             <div className="text-[9px] font-black text-white/20 uppercase tracking-widest mt-1">Found</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.01] border border-white/[0.03]">
                             <div className="text-xl font-black text-emerald-400 tabular-nums tracking-tighter">{s.ready_count ?? "?"}</div>
                             <div className="text-[9px] font-black text-white/20 uppercase tracking-widest mt-1">Ready</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.03] border border-lo-violet/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer shadow-[0_0_15px_rgba(123,47,255,0.1)] active:scale-95"
                             onClick={() => window.location.href=`/leados/outreach?session=${s.session_id}`}>
                             <ArrowRight className="w-5 h-5 text-lo-violet" />
                        </div>
                    </div>

                    <div className="flex items-center gap-3 pt-6 border-t border-white/5">
                        <div className="flex-1 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap overflow-hidden">
                             <span className="text-[9px] font-black text-lo-cyan uppercase tracking-widest animate-pulse">Transmission Ready</span>
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); deleteSession(s.session_id); }}
                            className="p-3 rounded-xl bg-red-500/5 border border-red-500/10 text-red-500/30 hover:text-red-500 hover:bg-red-500/10 transition-all opacity-20 hover:opacity-100"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
