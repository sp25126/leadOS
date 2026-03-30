"use client";

import { useEffect, useState } from "react";
import GlassCard from "@/components/ui/GlassCard";
import { apiGet, apiDelete } from "@/lib/api";
import { useBYOKStore } from "@/lib/byok-store";
import {
  Calendar,
  MapPin,
  Users,
  Zap,
  Trash2,
  ExternalLink,
  ChevronDown,
  Clock,
  Search,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface Session {
  session_id: string;
  business_type: string;
  location: string;
  radius_km: number;
  leads_count: number;
  created_at: string;
  ready_count?: number; // Calculated on fly or from DB
}

export default function SessionHistory() {
  const { keys } = useBYOKStore();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await apiGet("/api/leads/history", keys);
      setSessions(data.sessions || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await apiDelete(`/api/leads/session/${id}`, keys);
      setSessions((s) => s.filter((item) => item.session_id !== id));
      toast.success("Terminal clean! Discovery session purged.");
    } catch (e) {
      toast.error("Operation failed.");
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  if (loading) {
    return (
       <div className="flex flex-col items-center justify-center py-20 grayscale opacity-40">
          <Clock className="w-12 h-12 text-white animate-pulse" />
          <span className="text-[10px] font-black uppercase tracking-[0.3em] mt-6">Indexing History Clusters...</span>
       </div>
    );
  }

  if (sessions.length === 0) {
    return (
       <div className="text-center py-20 bg-white/[0.01] border border-dashed border-white/5 rounded-3xl">
          <Search className="w-8 h-8 text-white/10 mx-auto mb-4" />
          <p className="text-sm font-bold text-white/20 uppercase tracking-widest">No discovery recordings located.</p>
       </div>
    );
  }

  return (
    <div className="relative space-y-4">
      {/* Timeline line */}
      <div className="absolute left-[34px] top-6 bottom-6 w-px bg-white/[0.05]" />

      {sessions.map((s, i) => (
        <motion.div
          key={s.session_id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
          className="relative pl-16"
        >
          {/* Timeline Dot */}
          <div className="absolute left-[30px] top-6 w-2 h-2 rounded-full border border-white/20 bg-zinc-950 z-10 group-hover:scale-125 transition-transform" />

          <GlassCard
             className={cn("p-6 hover:border-leados-violet/20 transition-all cursor-pointer", expandedId === s.session_id && "border-leados-violet/40")}
             onClick={() => setExpandedId(expandedId === s.session_id ? null : s.session_id)}
          >
             <div className="flex flex-wrap items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                   <div className="w-12 h-12 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center text-white/40">
                      <Zap className="w-6 h-6" />
                   </div>
                   <div className="flex flex-col">
                      <span className="text-sm font-bold text-white flex items-center gap-2">
                         {s.business_type} 
                         <span className="text-white/20">in</span>
                         <span className="text-leados-cyan">{s.location}</span>
                      </span>
                      <span className="text-[10px] text-white/20 uppercase font-black tracking-widest mt-1">
                         {new Date(s.created_at).toLocaleDateString()} at {new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                   </div>
                </div>

                <div className="flex items-center gap-8">
                   <div className="flex flex-col items-center">
                      <span className="text-[10px] text-white/20 uppercase font-black tracking-widest mb-1">Leads</span>
                      <span className="text-sm font-bold text-white tabular-nums">{s.leads_count}</span>
                   </div>
                   <div className="flex flex-col items-center">
                      <span className="text-[10px] text-white/20 uppercase font-black tracking-widest mb-1">Status</span>
                      <span className="text-xs font-bold text-emerald-400">Archived</span>
                   </div>
                   <ChevronDown className={cn("w-5 h-5 text-white/10 transition-transform", expandedId === s.session_id && "rotate-180")} />
                </div>
             </div>

             <AnimatePresence>
                {expandedId === s.session_id && (
                   <motion.div
                     initial={{ height: 0, opacity: 0 }}
                     animate={{ height: "auto", opacity: 1 }}
                     exit={{ height: 0, opacity: 0 }}
                     className="overflow-hidden mt-8 pt-8 border-t border-white/5"
                   >
                     <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 text-xs">
                        <div className="space-y-4">
                           <div className="flex items-center gap-3">
                              <MapPin className="w-4 h-4 text-white/20" />
                              <span className="text-white/40">Cluster Radius:</span>
                              <span className="text-white font-bold">{s.radius_km} KM</span>
                           </div>
                           <div className="flex items-center gap-3">
                              <Users className="w-4 h-4 text-white/20" />
                              <span className="text-white/40">Discovery Score:</span>
                              <span className="text-leados-violet font-bold">High Fidelity</span>
                           </div>
                        </div>
                        <div className="flex items-end justify-end gap-3">
                           <button onClick={(e) => { e.stopPropagation(); handleDelete(s.session_id); }} className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-red-500/20 text-red-500/60 hover:text-red-500 hover:bg-red-500/5 transition-all uppercase text-[10px] font-black tracking-widest">
                              <Trash2 className="w-3.5 h-3.5" />
                              Purge Recording
                           </button>
                           <a href="/leados/leads" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-leados-violet border border-leados-violet shadow-[0_0_20px_rgba(123,47,255,0.3)] text-white hover:bg-leados-violet/80 transition-all uppercase text-[10px] font-black tracking-widest">
                              <ExternalLink className="w-3.5 h-3.5" />
                              Inspect Cluster
                           </a>
                        </div>
                     </div>
                   </motion.div>
                )}
             </AnimatePresence>
          </GlassCard>
        </motion.div>
      ))}
    </div>
  );
}
