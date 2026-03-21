"use client";

import { useEffect, useState } from "react";
import GlassCard from "@/components/ui/GlassCard";
import SendButton from "@/components/ui/SendButton";
import { apiGet, apiPost } from "@/lib/api";
import { useBYOKStore } from "@/lib/byok-store";
import {
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  ChevronDown,
  Users
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function OutreachPanel() {
  const { keys } = useBYOKStore();
  const [sessions, setSessions] = useState<any[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState("");
  const [stats, setStats] = useState({ total: 0, sent: 0, failed: 0 });
  const [running, setRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const fetchHistory = async () => {
    try {
      const data = await apiGet("/api/leads/history", keys);
      setSessions(data.sessions || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleStart = async () => {
    if (!selectedSessionId) {
      toast.error("MISSION ABORT: Select a valid session cluster first.");
      throw new Error("No session id");
    }
    
    setRunning(true);
    setLogs((v) => [`[COMMAND] INITIATING OUTREACH MISSION: ${selectedSessionId}`, ...v]);
    
    // Simulate campaign start
    await new Promise(r => setTimeout(r, 800));
    setLogs((v) => [`[PIPELINE] Grid synchronization started...`, ...v]);
    
    await new Promise(r => setTimeout(r, 600));
    setLogs((v) => [`[PIPELINE] Initializing SMTP relay...`, ...v]);
    
    await new Promise(r => setTimeout(r, 500));
    setLogs((v) => [`[PIPELINE] Routing via WhatsApp Business API...`, ...v]);

    try {
      // In a real scenario, this would be a long polling or websocket connection
      // For now we simulate the payload deployment
      await new Promise(r => setTimeout(r, 1000));
      setStats({ total: 120, sent: 45, failed: 1 });
      setLogs((v) => [`[SUCCESS] Transmission established. Cluster #4 active.`, ...v]);
    } catch (e) {
      toast.error("CAMPAIGN INJECTION FAILURE.");
      setRunning(false);
      throw e;
    } finally {
      // We don't setRunning(false) immediately because the campaign "continues" in the background
      // But for the button state, we return the promise
    }
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
        
        {/* Session Selection Console */}
        <section className="lg:col-span-2 space-y-8 h-full">
          <GlassCard className="p-8 h-full border-leados-violet/20 shadow-[0_0_80px_rgba(123,47,255,0.05)]" tilt>
            <div className="flex items-center gap-3 mb-8">
                 <div className="w-8 h-px bg-white/20" />
                 <h3 className="text-xs font-black text-leados-violet uppercase tracking-[0.3em]">
                    Target Cluster Protocol
                 </h3>
            </div>
            
            <div className="relative group mb-10">
              <select
                value={selectedSessionId}
                onChange={(e) => setSelectedSessionId(e.target.value)}
                className="w-full appearance-none bg-white/[0.03] border border-white/10 rounded-2xl px-8 py-5 text-sm font-bold text-white focus:outline-none focus:border-leados-violet/50 transition-all cursor-pointer shadow-inner"
              >
                <option value="" className="bg-zinc-950 font-bold">Select Active Discovery Session...</option>
                {sessions.map((s) => (
                  <option key={s.session_id} value={s.session_id} className="bg-zinc-950 text-white font-medium">
                    {s.business_type} in {s.location} — {s.leads_count} Leads Intercepted
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-8 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20 group-hover:text-leados-violet transition-colors pointer-events-none" />
            </div>

            <div className="flex flex-col md:flex-row items-center justify-between gap-8 pt-10 border-t border-white/5">
              <div className="flex flex-col items-center md:items-start">
                  <span className="text-[10px] font-black text-white/30 uppercase tracking-widest mb-1">Status Code</span>
                  <div className="flex items-center gap-2">
                       <span className={`w-2 h-2 rounded-full ${running ? "bg-emerald-400 animate-pulse" : "bg-white/10"}`} />
                       <span className="text-xs font-bold text-white/50">{running ? "COLD LAUNCH ACTIVE" : "TERMINAL STANDBY"}</span>
                  </div>
              </div>

              <div className="flex items-center gap-6">
                <button
                    onClick={() => {
                        setRunning(false);
                        setLogs((v) => [`[ABORT] MISSION CANCELLED BY OPERATOR`, ...v]);
                    }}
                    className="text-[10px] font-black text-white/20 hover:text-red-500 transition-colors uppercase tracking-[0.2em]"
                >
                    Manual Abort
                </button>
                <SendButton
                    label="Deploy Payload"
                    onClick={handleStart}
                    disabled={running && stats.sent > 0}
                    className="h-16 px-10 shadow-2xl"
                />
              </div>
            </div>
          </GlassCard>
        </section>

        {/* Live Command Stream */}
        <section className="h-full">
            <GlassCard className="h-full flex flex-col p-8 border-leados-cyan/20 shadow-[0_0_80px_rgba(0,229,255,0.05)]">
                <div className="flex items-center justify-between mb-8 border-b border-white/5 pb-6">
                    <div>
                        <h3 className="text-xs font-black text-white uppercase tracking-[0.2em]">Command Feed</h3>
                        <p className="text-[10px] font-bold text-white/20 mt-1 uppercase tracking-widest">Live Stream v2.4</p>
                    </div>
                    {running && <Loader2 className="w-4 h-4 text-leados-cyan animate-spin" />}
                </div>
                
                <div className="flex-1 overflow-y-auto space-y-4 font-mono text-[10px] pr-3 custom-scrollbar max-h-[450px]">
                    <AnimatePresence initial={false}>
                        {logs.length === 0 && (
                            <motion.span 
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="text-white/10 font-black uppercase tracking-[0.3em] block text-center py-20"
                            >
                                IO Stream Ready...
                            </motion.span>
                        )}
                        {logs.map((log, i) => (
                            <motion.div
                                key={i + log}
                                initial={{ opacity: 0, y: -15 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={cn(
                                    "p-3 rounded-xl border transition-all duration-500",
                                    log.includes("[COMMAND]") ? "bg-leados-violet/5 border-leados-violet/20 text-leados-violet" : 
                                    log.includes("[SUCCESS]") ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-400" :
                                    log.includes("[ABORT]") ? "bg-red-500/5 border-red-500/20 text-red-400" :
                                    "bg-white/[0.02] border-white/5 text-white/40"
                                )}
                            >
                                <span className="opacity-30 mr-2">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                                {log}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </GlassCard>
        </section>
      </div>

      {/* Grid Stats HUD */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: "Cluster Population", value: stats.total, icon: <Users className="w-5 h-5" />, gradient: "from-white/5 to-white/0" },
            { label: "Successful Transmissions", value: stats.sent, icon: <CheckCircle2 className="w-5 h-5" />, color: "text-emerald-400", gradient: "from-emerald-500/5 to-transparent" },
            { label: "Fault Detection", value: stats.failed, icon: <XCircle className="w-5 h-5" />, color: "text-red-400", gradient: "from-red-500/5 to-transparent" },
            { label: "In-Flight Queue", value: stats.total - stats.sent - stats.failed, icon: <Clock className="w-5 h-5" />, color: "text-leados-cyan", gradient: "from-leados-cyan/5 to-transparent" },
          ].map((s, i) => (
            <GlassCard key={i} className="p-6 relative group" tilt glow>
              <div className="flex items-center gap-4 mb-6">
                <div className={cn("p-2.5 rounded-xl bg-white/[0.03] border border-white/10", s.color || "text-white/40")}>
                  {s.icon}
                </div>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/30">{s.label}</span>
              </div>
              <div className={cn("text-4xl font-black tabular-nums tracking-tighter leading-none mb-2", s.color || "text-white")}>
                {s.value}
              </div>
              <div className={`absolute bottom-0 inset-x-0 h-1 hidden group-hover:block bg-gradient-to-r ${s.gradient}`} />
            </GlassCard>
          ))}
      </div>
    </div>
  );
}
