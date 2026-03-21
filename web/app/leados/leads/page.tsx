"use client";
import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import GlassCard from "@/components/ui/GlassCard";
import ActionButton from "@/components/ui/ActionButton";
import LeadOSLoader from "@/components/ui/LeadOSLoader";
import { useBYOKStore } from "@/lib/byok-store";
import { swrFetcher } from "@/lib/api";
import useSWR from "swr";
import {
  useReactTable, getCoreRowModel, getSortedRowModel,
  getFilteredRowModel, flexRender, ColumnDef, SortingState,
} from "@tanstack/react-table";
import { Phone, Mail, Globe, Users, Filter,
         Instagram, Facebook, ArrowUpDown, ExternalLink, ShieldCheck, MapPin } from "lucide-react";

// Score badge
const ScoreBadge = ({ score }: { score: number }) => {
  const color =
    score >= 8 ? "bg-lo-violet/20 text-lo-violet border-lo-violet/40 shadow-[0_0_12px_rgba(123,47,255,0.2)]" :
    score >= 5 ? "bg-lo-cyan/20 text-lo-cyan border-lo-cyan/40" :
                 "bg-white/[0.05] text-white/30 border-white/[0.08]";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black border uppercase tracking-widest ${color}`}>
      {score}/10
    </span>
  );
};

// Status badge
const StatusBadge = ({ status }: { status: string }) => {
  const map: Record<string, string> = {
    READY:   "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    NEW:     "bg-white/[0.04] text-white/40 border-white/[0.08]",
    PARTIAL: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    CLOSED:  "bg-red-500/10 text-red-400 border-red-500/30",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-black border uppercase tracking-widest ${map[status] || map.NEW}`}>
      {status}
    </span>
  );
};

export default function LeadsPage() {
  const { keys } = useBYOKStore();
  const { data, isLoading } = useSWR("/api/leads", swrFetcher(keys), { refreshInterval: 60000 });
  const leads = data?.leads ?? [];

  const [sorting, setSorting] = useState<SortingState>([{ id: "score", desc: true }]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const filtered = useMemo(() =>
    statusFilter === "ALL" ? leads : leads.filter((l: any) => l.status === statusFilter),
    [leads, statusFilter]
  );

  const columns: ColumnDef<any>[] = [
    { accessorKey: "name",   header: "Business Discovery",
      cell: info => (
        <div className="flex flex-col">
            <span className="text-white text-sm font-black uppercase tracking-tight leading-none mb-1">{info.getValue() as string}</span>
            <span className="text-[10px] text-white/20 font-bold uppercase tracking-widest font-mono">#{info.row.original.id?.slice(0,8)}</span>
        </div>
      )
    },
    { accessorKey: "score",  header: ({ column }) => (
        <button onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="flex items-center gap-2 text-white/30 hover:text-white text-[10px] font-black uppercase tracking-[0.2em]">
          Priority <ArrowUpDown className="w-3.5 h-3.5" />
        </button>
      ),
      cell: info => <ScoreBadge score={info.getValue() as number} />,
    },
    { accessorKey: "status", header: "Protocol Status",
      cell: info => <StatusBadge status={info.getValue() as string} />,
    },
    { accessorKey: "phone",  header: "Comms Channel",
      cell: info => info.getValue()
        ? <a href={`tel:${info.getValue()}`} className="text-lo-cyan text-xs font-bold hover:underline flex items-center gap-2"><Phone className="w-3.5 h-3.5" />{info.getValue() as string}</a>
        : <span className="text-white/10 text-[10px] font-black uppercase tracking-widest">— OFFLINE</span>,
    },
    { accessorKey: "email",  header: "Signal Transmission",
      cell: info => info.getValue()
        ? <a href={`mailto:${info.getValue()}`} className="text-lo-pink text-xs font-bold hover:underline flex items-center gap-2"><Mail className="w-3.5 h-3.5" />{(info.getValue() as string).slice(0,24)}…</a>
        : <span className="text-white/10 text-[10px] font-black uppercase tracking-widest">— UNDISCOVERED</span>,
    },
    { accessorKey: "website", header: "Grid Node",
      cell: info => info.getValue()
        ? <a href={info.getValue() as string} target="_blank" className="text-white/40 hover:text-lo-cyan transition-colors"><ExternalLink className="w-4 h-4" /></a>
        : <span className="text-white/10">—</span>,
    },
  ];

  const table = useReactTable({
    data: filtered, columns, state: { sorting, globalFilter },
    onSortingChange: setSorting, onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      <LeadOSLoader size="lg" label="Synchronizing Intelligence Base..." />
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <div className="flex flex-col md:flex-row items-center justify-between mb-10 gap-6">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-black text-lo-violet uppercase tracking-[0.3em] mb-4">
              <ShieldCheck className="w-4 h-4" /> Strategic Leads Base
          </div>
          <h1 className="text-4xl font-black text-white tracking-tighter uppercase mb-2 leading-none">Intelligence <span className="gradient-text">CRM</span></h1>
          <p className="text-white/30 text-sm font-medium uppercase tracking-widest">{leads.length} Records Intercepted · {leads.filter((l:any)=>l.status==="READY").length} Optimal Targets</p>
        </div>
        <ActionButton variant="violet" onClick={() => window.location.href="/leados/hunt"} className="h-14 px-8">
          <Users className="w-5 h-5 mr-1" />
          Initialize New Hunt
        </ActionButton>
      </div>

      {/* Control Filters HUD */}
      <GlassCard className="p-6 mb-8 border-white/10" glow>
        <div className="flex flex-col md:flex-row items-center gap-8 justify-between">
          <div className="flex items-center gap-4 flex-1 w-full bg-white/[0.03] border border-white/[0.08] rounded-2xl px-6 py-3 shadow-inner">
            <Filter className="w-4 h-4 text-white/30 flex-shrink-0" />
            <input
              value={globalFilter}
              onChange={e => setGlobalFilter(e.target.value)}
              placeholder="FILTER COMMANDS (NAME, LOCATION, DOMAIN)..."
              className="bg-transparent text-white text-[11px] font-black uppercase tracking-[0.2em] placeholder-white/15 outline-none w-full"
            />
          </div>
          <div className="flex gap-3 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 scrollbar-none">
            {["ALL","READY","NEW","PARTIAL"].map(s => (
              <button key={s} onClick={() => setStatusFilter(s)}
                className={`text-[10px] font-black uppercase tracking-[0.2em] px-5 py-2.5 rounded-xl border transition-all ${
                  statusFilter===s ? "bg-lo-violet/10 border-lo-violet/40 text-lo-violet shadow-[0_0_15px_rgba(123,47,255,0.1)]" : "border-white/[0.05] text-white/20 hover:border-white/20 hover:text-white/50"
                }`}>{s}</button>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* Database Table Rendering */}
      <GlassCard className="border-white/5 overflow-hidden" glow>
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full">
            <thead>
              {table.getHeaderGroups().map(hg => (
                <tr key={hg.id} className="border-b border-white/[0.05] bg-white/[0.01]">
                  {hg.headers.map(h => (
                    <th key={h.id} className="text-left px-6 py-5 text-[10px] text-white/30 uppercase tracking-[0.3em] font-black">
                      {flexRender(h.column.columnDef.header, h.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row, i) => (
                <motion.tr
                  key={row.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03, duration: 0.4 }}
                  className="border-b border-white/[0.03] hover:bg-white/[0.03] cursor-pointer transition-all duration-300 group"
                >
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-6 py-6 backdrop-blur-sm group-hover:backdrop-blur-none">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </motion.tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <div className="py-24 text-center">
              <LeadOSLoader size="sm" label="No intel records found — Initiate collection command" />
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
