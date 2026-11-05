import React, { useState } from "react";
import {
  CheckCircle2,
  Clock,
  SkipForward,
  XCircle,
  Activity,
  Layers,
  ChevronDown,
  ChevronRight,
  Info,
  Search,
} from "lucide-react";
import { IRMethodState, MethodStatus } from "../types/ir";

interface MethodDashboardProps {
  methods: IRMethodState[];
  onSelectMethod: (method: IRMethodState) => void;
}

export const MethodDashboard: React.FC<MethodDashboardProps> = ({
  methods,
  onSelectMethod,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>("ALL");
  const [searchFilter, setSearchFilter] = useState<string>("");
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({});

  // Group methods by category
  const categories = [
    "A. Text Processing & Normalization",
    "B. Index Construction",
    "C. Index Optimization & Compression",
    "D. Query Processing & Search",
    "E. Ranked Retrieval",
    "F. Search Improvement & Evaluation",
  ];

  const toggleCategory = (cat: string) => {
    setCollapsedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }));
  };

  const filteredMethods = methods.filter((m) => {
    const matchesCat = filterCategory === "ALL" || m.category === filterCategory;
    const matchesQuery =
      searchFilter === "" ||
      m.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      m.description.toLowerCase().includes(searchFilter.toLowerCase()) ||
      `#${m.id}`.includes(searchFilter);
    return matchesCat && matchesQuery;
  });

  const getStatusBadge = (status: MethodStatus) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 font-medium">
            <CheckCircle2 className="h-3 w-3" /> COMPLETED
          </span>
        );
      case "RUNNING":
        return (
          <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/80 font-medium animate-pulse">
            <Clock className="h-3 w-3 animate-spin" /> RUNNING
          </span>
        );
      case "SKIPPED":
        return (
          <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-700/80 font-medium">
            <SkipForward className="h-3 w-3" /> SKIPPED
          </span>
        );
      case "FAILED":
        return (
          <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-red-950/80 text-red-400 border border-red-800/80 font-medium">
            <XCircle className="h-3 w-3" /> FAILED
          </span>
        );
      case "PENDING":
      default:
        return (
          <span className="flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-500 border border-slate-800 font-medium">
            <Clock className="h-3 w-3" /> PENDING
          </span>
        );
    }
  };

  const completedCount = methods.filter((m) => m.status === "COMPLETED").length;
  const skippedCount = methods.filter((m) => m.status === "SKIPPED").length;
  const runningCount = methods.filter((m) => m.status === "RUNNING").length;

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl space-y-5">
      {/* Header and Summary Counters */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100 uppercase tracking-wide">
              Information Retrieval Pipeline (All 45+ Methods)
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Complete architectural matrix of indexing-time and query-time IR algorithms.
          </p>
        </div>

        {/* Status Counters */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-lg text-emerald-300">
            Completed: <span className="font-bold">{completedCount}</span>
          </div>
          <div className="bg-zinc-900 border border-zinc-700/60 px-2.5 py-1 rounded-lg text-zinc-300">
            Skipped: <span className="font-bold">{skippedCount}</span>
          </div>
          {runningCount > 0 && (
            <div className="bg-cyan-950/60 border border-cyan-800/60 px-2.5 py-1 rounded-lg text-cyan-300 animate-pulse">
              Running: <span className="font-bold">{runningCount}</span>
            </div>
          )}
          <div className="bg-slate-800 px-2.5 py-1 rounded-lg text-slate-300">
            Total: <span className="font-bold">{methods.length}</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-1 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0 text-xs">
          <button
            onClick={() => setFilterCategory("ALL")}
            className={`px-3 py-1.5 rounded-md font-medium transition-colors shrink-0 ${
              filterCategory === "ALL"
                ? "bg-cyan-600 text-white"
                : "bg-slate-800/80 text-slate-400 hover:text-slate-200"
            }`}
          >
            All Categories
          </button>
          {categories.map((cat, idx) => (
            <button
              key={idx}
              onClick={() => setFilterCategory(cat)}
              className={`px-2.5 py-1.5 rounded-md font-medium transition-colors shrink-0 ${
                filterCategory === cat
                  ? "bg-cyan-600 text-white"
                  : "bg-slate-800/80 text-slate-400 hover:text-slate-200"
              }`}
            >
              {cat.split(".")[0]}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="h-3.5 w-3.5 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Filter methods by name..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg py-1.5 pl-8 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>
      </div>

      {/* Grouped Methods Cards */}
      <div className="space-y-4">
        {categories
          .filter((cat) => filterCategory === "ALL" || filterCategory === cat)
          .map((cat) => {
            const catMethods = filteredMethods.filter((m) => m.category === cat);
            if (catMethods.length === 0) return null;
            const isCollapsed = collapsedCategories[cat];

            return (
              <div key={cat} className="bg-slate-950/60 border border-slate-800/80 rounded-xl overflow-hidden">
                {/* Category Header */}
                <div
                  onClick={() => toggleCategory(cat)}
                  className="bg-slate-800/40 px-4 py-2.5 flex items-center justify-between cursor-pointer hover:bg-slate-800/60 transition-colors border-b border-slate-800/60"
                >
                  <div className="flex items-center gap-2">
                    {isCollapsed ? (
                      <ChevronRight className="h-4 w-4 text-cyan-400" />
                    ) : (
                      <ChevronDown className="h-4 w-4 text-cyan-400" />
                    )}
                    <h3 className="text-xs font-bold text-slate-200 tracking-wide uppercase">{cat}</h3>
                    <span className="text-[11px] text-slate-400 font-mono">({catMethods.length} methods)</span>
                  </div>

                  <div className="flex items-center gap-2 text-[11px] font-mono">
                    <span className="text-emerald-400">
                      {catMethods.filter((m) => m.status === "COMPLETED").length} active
                    </span>
                  </div>
                </div>

                {/* Methods Grid */}
                {!isCollapsed && (
                  <div className="p-3 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {catMethods.map((method) => (
                      <div
                        key={method.id}
                        onClick={() => onSelectMethod(method)}
                        className="group bg-slate-900/80 hover:bg-slate-800/70 border border-slate-800 hover:border-cyan-500/50 rounded-lg p-3.5 cursor-pointer transition-all duration-200 flex flex-col justify-between"
                      >
                        <div>
                          {/* Method ID & Status */}
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-mono text-xs font-bold text-cyan-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                              #{method.id}
                            </span>
                            {getStatusBadge(method.status)}
                          </div>

                          {/* Method Name */}
                          <h4 className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">
                            {method.name}
                          </h4>

                          {/* Short Description */}
                          <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                            {method.description}
                          </p>

                          {/* Skipped Reason if skipped */}
                          {method.status === "SKIPPED" && method.reason_skipped && (
                            <div className="mt-2 bg-zinc-950/70 border border-zinc-800 rounded px-2 py-1 text-[11px] text-zinc-400">
                              <span className="font-semibold text-zinc-300">Reason:</span>{" "}
                              {method.reason_skipped}
                            </div>
                          )}
                        </div>

                        {/* Card Footer: Timing & Inputs */}
                        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-400">
                          <span>
                            {method.duration_ms > 0 ? (
                              <span className="text-cyan-400 font-semibold">{method.duration_ms.toFixed(1)}ms</span>
                            ) : (
                              "--"
                            )}
                          </span>

                          <span className="text-[10px] text-slate-400 group-hover:text-cyan-400 flex items-center gap-1 transition-colors">
                            <Info className="h-3 w-3" /> Details
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
      </div>
    </div>
  );
};
