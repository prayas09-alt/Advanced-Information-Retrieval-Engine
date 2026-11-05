import React, { useState, useEffect, useRef } from "react";
import {
  Terminal as TerminalIcon,
  Trash2,
  ArrowDown,
  Pause,
  Play,
  Maximize2,
  Minimize2,
  Filter,
  Info,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  SkipForward,
} from "lucide-react";
import { ExecutionEvent, MethodStatus } from "../types/ir";

interface LiveTerminalProps {
  events: ExecutionEvent[];
  onClear: () => void;
  onSelectEvent: (event: ExecutionEvent) => void;
}

export const LiveTerminal: React.FC<LiveTerminalProps> = ({
  events,
  onClear,
  onSelectEvent,
}) => {
  const [autoScroll, setAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [activeTab, setActiveTab] = useState<"terminal" | "trace" | "json">("terminal");
  const [filterLevel, setFilterLevel] = useState<string>("ALL");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Buffer events when paused
  const [displayedEvents, setDisplayedEvents] = useState<ExecutionEvent[]>([]);

  useEffect(() => {
    if (!isPaused) {
      setDisplayedEvents(events);
    }
  }, [events, isPaused]);

  useEffect(() => {
    if (autoScroll && !isPaused && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [displayedEvents, autoScroll, isPaused]);

  const filteredEvents = displayedEvents.filter((e) => {
    if (filterLevel === "ALL") return true;
    if (filterLevel === "COMPLETED") return e.status === "COMPLETED";
    if (filterLevel === "SKIPPED") return e.status === "SKIPPED";
    if (filterLevel === "ERROR") return e.status === "FAILED" || e.level === "ERROR";
    return true;
  });

  const getStatusColor = (status: MethodStatus) => {
    switch (status) {
      case "COMPLETED":
        return "text-emerald-400 bg-emerald-950/40 border-emerald-800/60";
      case "RUNNING":
        return "text-cyan-400 bg-cyan-950/40 border-cyan-800/60 animate-pulse";
      case "SKIPPED":
        return "text-zinc-400 bg-zinc-900/60 border-zinc-700/60";
      case "FAILED":
        return "text-red-400 bg-red-950/40 border-red-800/60";
      case "PENDING":
      default:
        return "text-slate-400 bg-slate-900/40 border-slate-700/60";
    }
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case "SYSTEM":
        return "text-purple-400";
      case "FILE":
        return "text-amber-400";
      case "PREPROCESSING":
        return "text-blue-400";
      case "INDEXING":
        return "text-cyan-400";
      case "COMPRESSION":
        return "text-teal-400";
      case "QUERY":
      case "QUERY_PROCESSING":
        return "text-sky-400";
      case "RANKING":
        return "text-emerald-400";
      case "QUERY_EXPANSION":
        return "text-fuchsia-400";
      case "ADVANCED_IR":
        return "text-indigo-400";
      case "EVALUATION":
        return "text-rose-400";
      case "COMPLETE":
        return "text-green-400";
      default:
        return "text-slate-400";
    }
  };

  const getStatusIcon = (status: MethodStatus) => {
    switch (status) {
      case "COMPLETED":
        return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />;
      case "RUNNING":
        return <Clock className="h-3.5 w-3.5 text-cyan-400 shrink-0 animate-spin" />;
      case "SKIPPED":
        return <SkipForward className="h-3.5 w-3.5 text-zinc-400 shrink-0" />;
      case "FAILED":
        return <XCircle className="h-3.5 w-3.5 text-red-400 shrink-0" />;
      default:
        return <Clock className="h-3.5 w-3.5 text-slate-500 shrink-0" />;
    }
  };

  return (
    <div
      className={`bg-[#090d16] border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex flex-col font-mono transition-all duration-300 ${
        isFullscreen ? "fixed inset-3 z-50 shadow-2xl border-cyan-500/40" : "h-[540px]"
      }`}
    >
      {/* VS Code Style Header Bar */}
      <div className="bg-[#0f1422] border-b border-slate-800/80 px-4 py-2.5 flex items-center justify-between select-none">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-red-500/80 inline-block" />
            <span className="h-3 w-3 rounded-full bg-yellow-500/80 inline-block" />
            <span className="h-3 w-3 rounded-full bg-green-500/80 inline-block" />
          </div>

          <div className="h-4 w-px bg-slate-700/60 mx-1" />

          {/* Terminal Tabs */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab("terminal")}
              className={`px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "terminal"
                  ? "bg-slate-800 text-cyan-300 border border-slate-700"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <TerminalIcon className="h-3 w-3" />
              LIVE EXECUTION TERMINAL
            </button>
            <button
              onClick={() => setActiveTab("trace")}
              className={`px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "trace"
                  ? "bg-slate-800 text-cyan-300 border border-slate-700"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              METHOD TRACE ({filteredEvents.filter((e) => e.method_id).length})
            </button>
            <button
              onClick={() => setActiveTab("json")}
              className={`px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5 ${
                activeTab === "json"
                  ? "bg-slate-800 text-cyan-300 border border-slate-700"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              RAW JSON
            </button>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-2">
          {/* Filter */}
          <div className="flex items-center gap-1 text-[11px] text-slate-400 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
            <Filter className="h-3 w-3" />
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="bg-transparent text-slate-300 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Events ({displayedEvents.length})</option>
              <option value="COMPLETED">Completed</option>
              <option value="SKIPPED">Skipped</option>
              <option value="ERROR">Errors</option>
            </select>
          </div>

          {/* Pause / Resume */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-1.5 rounded transition-colors text-xs flex items-center gap-1 ${
              isPaused
                ? "bg-amber-950 text-amber-300 border border-amber-800"
                : "bg-slate-800/80 hover:bg-slate-700 text-slate-300"
            }`}
            title={isPaused ? "Resume real-time logs" : "Pause log stream"}
          >
            {isPaused ? <Play className="h-3.5 w-3.5 text-amber-400" /> : <Pause className="h-3.5 w-3.5" />}
          </button>

          {/* Auto Scroll Toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`p-1.5 rounded transition-colors text-xs ${
              autoScroll
                ? "bg-cyan-950 text-cyan-400 border border-cyan-800"
                : "bg-slate-800/80 hover:bg-slate-700 text-slate-400"
            }`}
            title={autoScroll ? "Auto-scroll ON" : "Auto-scroll OFF"}
          >
            <ArrowDown className="h-3.5 w-3.5" />
          </button>

          {/* Clear Terminal */}
          <button
            onClick={onClear}
            className="p-1.5 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Clear terminal logs"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
          </button>
        </div>
      </div>

      {/* Terminal Body Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-1.5 select-text text-xs leading-relaxed">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 py-12">
            <TerminalIcon className="h-8 w-8 mb-2 opacity-50" />
            <p>Live search engine terminal ready.</p>
            <p className="text-[11px] text-slate-600 mt-1">
              Upload a document or execute a search query to stream live backend execution logs.
            </p>
          </div>
        ) : activeTab === "terminal" ? (
          filteredEvents.map((evt, idx) => (
            <div
              key={evt.id || idx}
              onClick={() => onSelectEvent(evt)}
              className="group flex items-start gap-2.5 py-1 px-2 rounded hover:bg-slate-800/50 cursor-pointer transition-colors border border-transparent hover:border-slate-700/60"
            >
              {/* Timestamp */}
              <span className="text-slate-500 select-none shrink-0 font-mono text-[11px]">
                [{evt.timestamp}]
              </span>

              {/* Status Icon */}
              <span className="mt-0.5">{getStatusIcon(evt.status)}</span>

              {/* Stage Tag */}
              <span className={`font-semibold shrink-0 uppercase text-[11px] ${getStageColor(evt.stage)}`}>
                {evt.stage}:
              </span>

              {/* Method ID Badge if catalog method */}
              {evt.method_id && (
                <span className="bg-slate-800 text-cyan-300 text-[10px] px-1.5 py-0.2 rounded border border-slate-700 shrink-0">
                  M{evt.method_id}
                </span>
              )}

              {/* Message */}
              <span
                className={`flex-1 break-words ${
                  evt.status === "FAILED"
                    ? "text-red-300 font-semibold"
                    : evt.status === "SKIPPED"
                    ? "text-zinc-400 italic"
                    : "text-slate-200"
                }`}
              >
                {evt.message}
              </span>

              {/* Status Pill */}
              <span
                className={`text-[10px] font-mono px-1.5 py-0.2 rounded border shrink-0 ${getStatusColor(
                  evt.status
                )}`}
              >
                {evt.status}
              </span>

              {/* Duration in ms */}
              {evt.duration_ms !== null && evt.duration_ms !== undefined && (
                <span className="text-slate-500 text-[10px] shrink-0 font-mono">
                  {evt.duration_ms.toFixed(1)}ms
                </span>
              )}

              {/* Inspect Icon on Hover */}
              <Info className="h-3 w-3 text-cyan-400 opacity-0 group-hover:opacity-100 shrink-0 transition-opacity" />
            </div>
          ))
        ) : activeTab === "trace" ? (
          // Method Trace View: Table of methods only
          <div className="space-y-2">
            {filteredEvents
              .filter((e) => e.method_id)
              .map((e, idx) => (
                <div
                  key={idx}
                  onClick={() => onSelectEvent(e)}
                  className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 hover:border-cyan-500/50 cursor-pointer transition-all flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-cyan-400 font-bold bg-slate-800 px-2 py-1 rounded text-xs">
                      #{e.method_id}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-100">{e.method_name}</span>
                        <span className="text-[10px] text-slate-400">({e.stage})</span>
                      </div>
                      <p className="text-slate-400 text-[11px] mt-0.5">{e.message}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-0.5 rounded border ${getStatusColor(e.status)}`}>
                      {e.status}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {e.duration_ms ? `${e.duration_ms.toFixed(1)}ms` : "--"}
                    </span>
                  </div>
                </div>
              ))}
          </div>
        ) : (
          // Raw JSON View
          <pre className="text-xs text-cyan-300 font-mono bg-slate-950 p-4 rounded-lg overflow-x-auto border border-slate-800">
            {JSON.stringify(filteredEvents, null, 2)}
          </pre>
        )}

        <div ref={terminalEndRef} />
      </div>

      {/* Terminal Footer Bar */}
      <div className="bg-[#0f1422] border-t border-slate-800/80 px-4 py-1.5 flex items-center justify-between text-[11px] text-slate-500">
        <div className="flex items-center gap-3">
          <span>Stream: ws://127.0.0.1:8000/ws/execution</span>
          <span>•</span>
          <span>Events: {filteredEvents.length}</span>
          {isPaused && <span className="text-amber-400 font-bold">• [STREAM PAUSED]</span>}
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span>Click any line to inspect algorithm formulas & inputs</span>
        </div>
      </div>
    </div>
  );
};
