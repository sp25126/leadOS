"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import GlassCard from "@/components/ui/GlassCard";
import ActionButton from "@/components/ui/ActionButton";
import SendButton from "@/components/ui/SendButton";
import LeadOSLoader from "@/components/ui/LeadOSLoader";
import { useBYOKStore } from "@/lib/byok-store";
import { api, swrFetcher } from "@/lib/api";
import useSWR from "swr";
import { toast } from "sonner";
import { Send, Square, Activity, Mail, Users, AlertTriangle, RefreshCw, Zap, Clock, ShieldCheck, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export default function OutreachPage() {
  const { keys } = useBYOKStore();
  const { data: statusData, mutate: refetch } = useSWR(
    "/api/leads/outreach/status", swrFetcher(keys), { refreshInterval: 5000 }
  );
  const { data: histData } = useSWR("/api/leads/history", swrFetcher(keys));
  const sessions = histData?.sessions ?? [];

  const [selectedSession, setSelectedSession] = useState("");
  const [logs, setLogs] = useState<string[]>([]);

  const isRunning = statusData?.status === "running";
  const stats = statusData?.stats ?? { total:0, sent:0, failed:0, remaining:0 };

  const startOutreach = async () => {
    if (!selectedSession) { toast.error("MISSION ABORT: Select a valid session cluster first."); throw new Error("No session selected"); }
    await api.post("/api/leads/outreach/start", { session_id: selectedSession }, keys);
    toast.success("OUTREACH ENGAGED!");
    setLogs(l => [`[SYSTEM] [${new Date().toLocaleTimeString()}] Sequence initialized for ${selectedSession}`, ...l]);
    refetch();
  };

  const stopOutreach = async () => {
    await api.post("/api/leads/outreach/stop", {}, keys);
    toast.info("OUTREACH TERMINATED");
    setLogs(l => [`[SYSTEM] [${new Date().toLocaleTimeString()}] Sequence manually aborted by operator`, ...l]);
    refetch();
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="flex flex-col md:flex-row items-center justify-between mb-12 gap-6">
        <div>
            <div className="flex items-center gap-2 text-[10px] font-black text-lo-pink uppercase tracking-[0.3em] mb-4">
                <Send className="w-4 h-4" /> Strategic Transmission Control
            </div>
            <h1 className="text-4xl font-black text-white tracking-tighter uppercase mb-2 leading-none">Command <span className="gradient-text">Outreach</span></h1>
            <p className="text-white/30 text-sm font-medium uppercase tracking-widest leading-none">Signal Distribution Engine · Multi-Channel Signal Sync</p>
        </div>
        <div className="flex items-center gap-4">
            <ActionButton variant="white" onClick={() => refetch()} className="h-14 px-6 opacity-30 hover:opacity-100">
                <RefreshCw className={`w-4 h-4 ${isRunning ? "animate-spin" : ""}`} />
            </ActionButton>
            <div className={`px-4 py-2 rounded-xl border text-[10px] font-black uppercase tracking-widest ${isRunning ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-400 shadow-[0_0_20px_rgba(52,211,153,0.2)]" : "bg-white/5 border-white/10 text-white/20"}`}>
                <span className={`inline-block w-2.5 h-2.5 rounded-full mr-2 ${isRunning ? "bg-emerald-400 animate-pulse" : "bg-white/10"}`} />
                {isRunning ? "TRANS M ISSION ACTIVE" : "COMMAND IDLE"}
            </div>
        </div>
      </div>

      {/* Grid Stats HUD */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {[
          { l:"Signal Payload", v:stats.total,     i:<Users />,     c:"text-white/60",  g:"from-white/10 to-transparent" },
          { l:"Successful IO", v:stats.sent,      i:<CheckCircle2 />, i_c:"text-emerald-400", c:"text-emerald-400", g:"from-emerald-500/15 to-transparent shadow-[0_0_30px_rgba(16,185,129,0.1)]" },
          { l:"Signal Failure", v:stats.failed,    i:<XCircle />,   i_c:"text-lo-pink", c:"text-lo-pink", g:"from-pink-600/15 to-transparent" },
          { l:"Signal Queue",   v:stats.remaining, i:<Clock />,     i_c:"text-lo-cyan", c:"text-lo-cyan", g:"from-cyan-500/15 to-transparent" },
        ].map((s,i) => (
          <GlassCard key={s.l} delay={i*0.1} tilt glow className={`p-8 border-white/5 ${s.g}`}>
            <div className="flex items-center gap-4 mb-6">
                <div className={cn("w-10 h-10 rounded-xl flex items-center justify-center border border-white/10 bg-white/5", s.i_c || "text-white/40")}>
                    {s.i}
                </div>
                <div className="text-[10px] font-black uppercase tracking-[0.2em] text-white/20 leading-none">{s.l}</div>
            </div>
            <div className={cn("text-4xl font-black tabular-nums tracking-tighter leading-none", s.c)}>{s.v}</div>
          </GlassCard>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-stretch">
        
        {/* Sequence Control Console */}
        <section className="lg:col-span-12">
            <GlassCard className="p-10 border-white/10 shadow-[0_0_100px_rgba(255,45,155,0.04)]" glow tilt>
                <div className="flex items-center gap-4 mb-10">
                    <div className="w-10 h-px bg-white/10" />
                    <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-lo-pink">Sequence Logic Configuration</h3>
                </div>

                <div className="flex flex-col lg:flex-row items-center gap-10 justify-between">
                    <div className="flex-1 w-full relative group">
                        <label className="text-[9px] font-black uppercase tracking-[0.3em] text-white/20 mb-3 block">TARGET SESSION CLUSTER</label>
                        <select
                            value={selectedSession}
                            onChange={e => setSelectedSession(e.target.value)}
                            className="w-full appearance-none bg-white/[0.03] border border-white/[0.08] rounded-2xl px-8 py-5 text-sm font-black text-white focus:outline-none focus:border-lo-pink/50 transition-all cursor-pointer shadow-inner pr-16"
                        >
                            <option value="" className="bg-zinc-950 font-black">--- S ELECT ACTIVE DISCOVERY SESSION ---</option>
                            {sessions.map((s: any) => (
                                <option key={s.session_id} value={s.session_id} className="bg-zinc-950 text-white font-bold">
                                    {s.business_type} in {s.location} — [{s.ready_count ?? s.total_count ?? "?"} Units Detected]
                                </option>
                            ))}
                        </select>
                        <Zap className="absolute right-8 top-12 w-5 h-5 text-white/10 group-hover:text-lo-pink transition-colors pointer-events-none" />
                    </div>

                    <div className="flex items-center gap-6 pt-6">
                        {!isRunning ? (
                            <SendButton
                                onClick={startOutreach}
                                label="Deploy Protocol"
                                className="h-16 px-12 text-lg shadow-[0_0_50px_rgba(255,45,155,0.2)]"
                            />
                        ) : (
                            <ActionButton variant="white" onClick={stopOutreach} className="h-16 px-12 text-lg border-lo-pink/40 text-lo-pink bg-lo-pink/5 shadow-[0_0_50px_rgba(255,45,155,0.1)]">
                                <Square className="w-5 h-5 mr-1" /> Terminate OPS
                            </ActionButton>
                        )}
                    </div>
                </div>
            </GlassCard>
        </section>

        {/* Live IO Stream Console */}
        <section className="lg:col-span-12">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                <div className="lg:col-span-8">
                    <GlassCard className="p-10 border-white/10 h-full">
                        <div className="flex items-center justify-between mb-8 border-b border-white/5 pb-8">
                            <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-lo-cyan flex items-center gap-2">
                                <Activity className="w-4 h-4" /> Live Signal Transmission Command Feed
                            </h3>
                            {isRunning && (
                                <div className="text-[10px] font-black text-emerald-400/60 uppercase tracking-widest animate-pulse">
                                    [LINK ESTABLISHED]
                                </div>
                            )}
                        </div>

                        <div className="space-y-4 max-h-[400px] overflow-y-auto custom-scrollbar font-mono text-[10px] pr-4">
                            <AnimatePresence initial={false}>
                                {logs.length === 0 && (
                                    <div className="py-20 text-center opacity-10 font-black uppercase tracking-[0.5em]">Command Log Standby...</div>
                                )}
                                {logs.map((l, i) => (
                                    <motion.div 
                                        key={l + i} 
                                        initial={{ opacity:0, x:-20 }} animate={{ opacity:1, x:0 }}
                                        className={cn(
                                            "flex items-start gap-4 p-4 rounded-xl border border-white/5 bg-white/[0.01] group hover:bg-white/[0.03] transition-all",
                                            l.includes("[SYSTEM]") ? "border-lo-violet/20 bg-lo-violet/5" : "text-white/40"
                                        )}
                                    >
                                        <span className="text-[9px] font-black opacity-30 mt-0.5">0{logs.length - i}</span>
                                        <span className="flex-1 break-all tracking-[0.05em]">{l}</span>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </GlassCard>
                </div>

                {/* Progress HUD */}
                <div className="lg:col-span-4">
                    <GlassCard className="p-8 h-full border-white/10 flex flex-col justify-center text-center items-center">
                        <div className="mb-10 w-full">
                             <h3 className="text-[11px] font-black text-white uppercase tracking-[0.3em] mb-10">Transmit Signal Progress</h3>
                             
                             <div className="relative w-48 h-48 mx-auto flex items-center justify-center">
                                 {/* Circular progress bar */}
                                 <svg className="absolute inset-0 w-full h-full -rotate-90">
                                     <circle cx="96" cy="96" r="88" className="fill-none stroke-white/5 stroke-[8]" />
                                     <motion.circle 
                                         cx="96" cy="96" r="88" 
                                         className="fill-none stroke-lo-pink stroke-[8]" 
                                         style={{ strokeDasharray: 552.92, pathLength: 100 }}
                                         animate={{ strokeDashoffset: 100 - (stats.total > 0 ? (stats.sent/stats.total)*100 : 0) }}
                                         transition={{ duration: 1, ease: "easeOut" }}
                                     />
                                 </svg>
                                 
                                 {isRunning ? (
                                    <LeadOSLoader size="sm" />
                                 ) : (
                                    <div className="text-4xl font-black text-white tracking-tighter tabular-nums">
                                        {stats.total > 0 ? Math.round((stats.sent/stats.total)*100) : 0}<span className="text-sm opacity-20 font-black tracking-widest ml-1">%</span>
                                    </div>
                                 )}
                             </div>
                        </div>

                        <div className="space-y-4 w-full pt-10 border-t border-white/5">
                             <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-white/30">
                                 <span>Sequence Pulse</span>
                                 <span className="text-white/60">{stats.sent} / {stats.total} Pkts</span>
                             </div>
                             <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                 <motion.div 
                                    className="h-full bg-lo-pink"
                                    animate={{ width: `${stats.total > 0 ? (stats.sent/stats.total)*100 : 0}%` }}
                                 />
                             </div>
                        </div>
                    </GlassCard>
                </div>
            </div>
        </section>

      </div>
    </div>
  );
}
