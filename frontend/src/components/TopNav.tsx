import React from "react";
import { Terminal, Database, Activity, FileText, CheckCircle2, Cpu } from "lucide-react";
import { IndexStatus } from "../types/ir";

interface TopNavProps {
  indexStatus: IndexStatus | null;
  isConnected: boolean;
  activeView: "search" | "methods" | "terminal" | "analytics";
  setActiveView: (view: "search" | "methods" | "terminal" | "analytics") => void;
  onOpenSampleModal: () => void;
  onOpenEvalModal: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  indexStatus,
  isConnected,
  activeView,
  setActiveView,
  onOpenSampleModal,
  onOpenEvalModal,
}) => {
  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-4 lg:px-6 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-100 text-base tracking-tight">ARGUS IR</span>
                <span className="text-[10px] font-semibold uppercase tracking-wider bg-cyan-950 text-cyan-400 border border-cyan-800/60 px-1.5 py-0.5 rounded">
                  45 IR Methods
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Advanced Information Retrieval Engine</p>
            </div>
          </div>

          {/* Connection Status Pill */}
          <div className="flex items-center gap-2">
            <div
              className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${
                isConnected
                  ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/60"
                  : "bg-amber-950/60 text-amber-400 border-amber-800/60"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${
                  isConnected ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
                }`}
              />
              <span className="font-mono text-[11px] font-medium">
                {isConnected ? "ENGINE ONLINE" : "CONNECTING..."}
              </span>
            </div>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center gap-1 bg-slate-950/80 p-1 rounded-lg border border-slate-800 text-xs font-medium">
          <button
            onClick={() => setActiveView("search")}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeView === "search"
                ? "bg-cyan-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <Database className="h-3.5 w-3.5" />
            Search & Results
          </button>
          <button
            onClick={() => setActiveView("methods")}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeView === "methods"
                ? "bg-cyan-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            IR Pipeline (45)
          </button>
          <button
            onClick={() => setActiveView("terminal")}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeView === "terminal"
                ? "bg-cyan-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            Live Terminal
          </button>
          <button
            onClick={() => setActiveView("analytics")}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeView === "analytics"
                ? "bg-cyan-600 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            Analytics
          </button>
        </div>

        {/* Active Document Status & Quick Actions */}
        <div className="flex items-center gap-2.5">
          {indexStatus?.indexed && indexStatus.metadata ? (
            <div className="hidden xl:flex items-center gap-2 bg-slate-800/60 border border-slate-700/60 px-3 py-1.5 rounded-lg text-xs">
              <FileText className="h-4 w-4 text-cyan-400" />
              <div className="text-left">
                <div className="flex items-center gap-1.5">
                  <span className="font-semibold text-slate-200 max-w-[140px] truncate">
                    {indexStatus.metadata.filename}
                  </span>
                  <span className="bg-slate-700 text-slate-300 text-[10px] px-1 py-0.2 rounded font-mono">
                    {indexStatus.metadata.extension}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">
                  {indexStatus.total_segments} passages | {indexStatus.vocabulary_size} terms
                </span>
              </div>
            </div>
          ) : (
            <span className="hidden xl:inline text-xs text-slate-500 font-mono italic">
              No document uploaded
            </span>
          )}

          <button
            onClick={onOpenSampleModal}
            className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <FileText className="h-3.5 w-3.5 text-cyan-400" />
            Samples
          </button>

          <button
            onClick={onOpenEvalModal}
            className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            Benchmark
          </button>
        </div>
      </div>
    </header>
  );
};
