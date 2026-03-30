"use client";

import { useEffect, useState, useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import { apiGet } from "@/lib/api";
import { useBYOKStore } from "@/lib/byok-store";
import {
  Search,
  Users,
  Filter,
  Download,
  Phone,
  Mail,
  MessageSquare,
  Globe,
  ExternalLink,
  ChevronRight,
  X,
  Zap,
} from "lucide-react";
import GlassCard from "@/components/ui/GlassCard";
import MagneticButton from "@/components/ui/MagneticButton";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface Lead {
  id: string;
  name: string;
  phone: string;
  email: string;
  website: string;
  score: number;
  status: "READY" | "NEW" | "PARTIAL";
  location: string;
  business_type: string;
  suggested_opening?: string;
  pain_points?: string[];
  socials?: {
    instagram?: string;
    facebook?: string;
  };
}

export default function LeadsTable() {
  const { keys } = useBYOKStore();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [globalFilter, setGlobalFilter] = useState("");

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const data = await apiGet("/api/leads/", keys);
      setLeads(data.leads || data); // Handle both wrapped and unwrapped response
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  const columnHelper = createColumnHelper<Lead>();

  const columns = useMemo(
    () => [
      columnHelper.accessor("name", {
        header: "Entity",
        cell: (info) => (
          <div className="flex flex-col">
            <span className="text-white font-medium">{info.getValue()}</span>
            <span className="text-[10px] text-white/20 uppercase tracking-widest leading-none mt-1">
              {info.row.original.business_type}
            </span>
          </div>
        ),
      }),
      columnHelper.accessor("location", {
        header: "Location",
        cell: (info) => <span className="text-white/40">{info.getValue()}</span>,
      }),
      columnHelper.accessor("score", {
        header: "AI Score",
        cell: (info) => {
          const score = info.getValue() || 0;
          const color =
            score >= 8
              ? "text-leados-violet drop-shadow-[0_0_8px_rgba(123,47,255,0.4)]"
              : score >= 5
              ? "text-leados-cyan"
              : "text-white/40";
          return (
            <div className={cn("flex items-center gap-1.5 font-bold", color)}>
              <Zap className="w-3 h-3 fill-current" />
              {score.toFixed(1)}
            </div>
          );
        },
      }),
      columnHelper.accessor("status", {
        header: "Status",
        cell: (info) => {
          const status = info.getValue();
          const theme =
            status === "READY"
              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
              : status === "PARTIAL"
              ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
              : "bg-white/5 text-white/30 border-white/10";
          return (
            <span
              className={cn(
                "px-2 py-0.5 rounded-full text-[10px] font-bold border",
                theme
              )}
            >
              {status}
            </span>
          );
        },
      }),
      columnHelper.display({
        id: "actions",
        header: "",
        cell: (info) => (
          <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            {info.row.original.phone && (
              <Phone className="w-3.5 h-3.5 text-white/20 hover:text-leados-cyan transition-colors cursor-pointer" />
            )}
            {info.row.original.email && (
              <Mail className="w-3.5 h-3.5 text-white/20 hover:text-leados-pink transition-colors cursor-pointer" />
            )}
            {info.row.original.website && (
              <Globe className="w-3.5 h-3.5 text-white/20 hover:text-leados-violet transition-colors cursor-pointer" />
            )}
            <ChevronRight className="w-4 h-4 text-white/10" />
          </div>
        ),
      }),
    ],
    []
  );

  const table = useReactTable({
    data: leads,
    columns,
    state: {
      globalFilter,
    },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div className="relative">
      {/* ── Controls ──────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" />
          <input
            type="text"
            value={globalFilter ?? ""}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search leads by name, city or niche..."
            className="w-full bg-white/[0.03] border border-white/[0.08] rounded-2xl pl-11 pr-4 py-3.5 text-sm text-white focus:outline-none focus:border-leados-violet/40 transition-colors"
          />
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-3 rounded-2xl bg-white/5 border border-white/10 text-xs font-medium text-white/60 hover:text-white transition-colors">
            <Filter className="w-4 h-4" />
            Configure Filters
          </button>
          <MagneticButton onClick={fetchLeads}>
            <Download className="w-4 h-4" />
            Export CSV
          </MagneticButton>
        </div>
      </div>

      {/* ── Table ─────────────────────────────────────── */}
      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr
                  key={headerGroup.id}
                  className="bg-white/[0.02] border-b border-white/[0.05]"
                >
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="text-left px-6 py-4 text-[11px] font-bold text-white/30 uppercase tracking-[0.15em]"
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={columns.length} className="py-20 text-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                      className="inline-block p-2 rounded-full border border-leados-violet/20"
                    >
                      <Zap className="w-6 h-6 text-leados-violet animate-pulse" />
                    </motion.div>
                    <p className="text-white/20 text-sm mt-4 tracking-widest uppercase">
                      Syncing CRM Database...
                    </p>
                  </td>
                </tr>
              ) : table.getRowModel().rows.length === 0 ? (
                <tr>
                   <td colSpan={columns.length} className="py-20 text-center text-white/20">
                      No leads discovered yet. Start a hunt!
                   </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => setSelectedLead(row.original)}
                    className="group border-b border-white/[0.03] hover:bg-white/[0.01] transition-colors cursor-pointer"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-6 py-5">
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* ── Detail Slide-over ─────────────────────────── */}
      <AnimatePresence>
        {selectedLead && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedLead(null)}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100]"
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed right-0 top-0 bottom-0 w-full max-w-xl bg-zinc-950 border-l border-white/10 z-[101] shadow-2xl"
            >
              <div className="h-full flex flex-col p-8 overflow-y-auto custom-scrollbar">
                <div className="flex items-center justify-between mb-8">
                  <span className="text-[10px] font-bold text-leados-violet uppercase tracking-[0.2em]">
                    Lead Enrichment Intelligence
                  </span>
                  <button
                    onClick={() => setSelectedLead(null)}
                    className="p-2 rounded-full hover:bg-white/5 transition-colors"
                  >
                    <X className="w-5 h-5 text-white/40" />
                  </button>
                </div>

                <div className="mb-10">
                  <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">
                    {selectedLead.name}
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-0.5 rounded-md bg-white/5 text-[10px] font-bold text-white/60">
                      {selectedLead.business_type}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-white/5 text-[10px] font-bold text-white/60">
                      {selectedLead.location}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-10">
                  <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                    <div className="text-[10px] text-white/20 uppercase font-black tracking-widest mb-1">
                      AI Quality Score
                    </div>
                    <div className="text-2xl font-black text-leados-violet">
                      {selectedLead.score?.toFixed(1) || "?.?"}
                    </div>
                  </div>
                  <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5">
                    <div className="text-[10px] text-white/20 uppercase font-black tracking-widest mb-1">
                      Status State
                    </div>
                    <div className="text-xl font-black text-white/80">
                      {selectedLead.status}
                    </div>
                  </div>
                </div>

                <div className="space-y-8">
                  <section>
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4">
                      Contact Metadata
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-white/[0.01]">
                        <span className="text-xs text-white/40">Phone Number</span>
                        <span className="text-xs text-white font-medium">
                          {selectedLead.phone || "Not Discovered"}
                        </span>
                      </div>
                      <div className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-white/[0.01]">
                        <span className="text-xs text-white/40">Email Domain</span>
                        <span className="text-xs text-white font-medium">
                          {selectedLead.email?.replace(/(?<=.{3}).(?=.*@)/g, "*") ||
                            "Enrichment Pending"}
                        </span>
                      </div>
                    </div>
                  </section>

                  <section>
                    <h3 className="text-xs font-bold text-leados-cyan uppercase tracking-widest mb-4">
                      AI Insights & Suggested Opening
                    </h3>
                    <div className="p-6 rounded-2xl border border-leados-cyan/20 bg-leados-cyan/[0.02] relative overflow-hidden">
                      <div className="relative z-10 italic text-sm text-white/70 leading-relaxed">
                        "{selectedLead.suggested_opening || "Initialize AI scoring to generate opening line."}"
                      </div>
                      <Zap className="absolute -right-4 -bottom-4 w-24 h-24 text-leados-cyan/10" />
                    </div>
                  </section>

                  <section>
                    <h3 className="text-xs font-bold text-white uppercase tracking-widest mb-4">
                      Pain points identified
                    </h3>
                    <div className="flex flex-wrap gap-2">
                       {selectedLead.pain_points?.map(p => (
                         <span key={p} className="px-3 py-1.5 rounded-lg bg-red-400/5 border border-red-400/10 text-[10px] font-bold text-red-400/60 lowercase">
                            # {p}
                         </span>
                       ))}
                    </div>
                  </section>
                </div>

                <div className="mt-auto pt-8 flex gap-3">
                   <MagneticButton className="flex-1">
                      <Send className="w-4 h-4" />
                      Trigger Outreach
                   </MagneticButton>
                   <button className="p-3.5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                      <ExternalLink className="w-5 h-5 text-white/60" />
                   </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

// Added Send icon to imports
import { Send } from "lucide-react";
