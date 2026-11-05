import React from "react";
import { X, CheckCircle2, Clock, SkipForward, XCircle, Code, Layers, FileCode } from "lucide-react";
import { ExecutionEvent, IRMethodState, MethodStatus } from "../types/ir";

interface MethodDetailModalProps {
  item: ExecutionEvent | IRMethodState | null;
  onClose: () => void;
}

export const MethodDetailModal: React.FC<MethodDetailModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  const isEvent = "stage" in item;
  const name = isEvent ? item.method_name : item.name;
  const methodId = isEvent ? item.method_id : item.id;
  const status: MethodStatus = item.status;
  const message = isEvent ? item.message : item.description;
  const duration = item.duration_ms;
  const details = item.details;
  const category = !isEvent ? item.category : undefined;
  const inputInfo = !isEvent ? item.input_info : undefined;
  const outputInfo = !isEvent ? item.output_info : undefined;
  const reasonSkipped = !isEvent ? item.reason_skipped : undefined;

  const getStatusColor = (st: MethodStatus) => {
    switch (st) {
      case "COMPLETED":
        return "text-emerald-400 bg-emerald-950/80 border-emerald-800";
      case "RUNNING":
        return "text-cyan-400 bg-cyan-950/80 border-cyan-800";
      case "SKIPPED":
        return "text-zinc-400 bg-zinc-900 border-zinc-700";
      case "FAILED":
        return "text-red-400 bg-red-950/80 border-red-800";
      default:
        return "text-slate-400 bg-slate-900 border-slate-700";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Modal Header */}
        <div className="bg-slate-900/80 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {methodId && (
              <span className="font-mono text-xs font-bold bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-1 rounded">
                Method #{methodId}
              </span>
            )}
            <div>
              <h3 className="text-base font-bold text-slate-100">{name}</h3>
              {category && <p className="text-xs text-slate-400 font-mono">{category}</p>}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className={`text-xs font-mono px-2.5 py-0.5 rounded-full border ${getStatusColor(status)}`}>
              {status}
            </span>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-4 text-sm leading-relaxed">
          {/* Status Alert Banner */}
          {status === "COMPLETED" && (
            <div className="bg-emerald-950/30 border border-emerald-800/60 rounded-xl p-3.5 flex items-start gap-3 text-xs text-emerald-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold text-emerald-200">Algorithm Executed Successfully</p>
                <p className="mt-0.5">{message}</p>
              </div>
            </div>
          )}

          {status === "SKIPPED" && (
            <div className="bg-zinc-900/60 border border-zinc-700/80 rounded-xl p-3.5 flex items-start gap-3 text-xs text-zinc-300">
              <SkipForward className="h-4 w-4 text-zinc-400 mt-0.5 shrink-0" />
              <div>
                <p className="font-semibold text-zinc-200">Algorithm Conditionally Skipped</p>
                <p className="mt-0.5">
                  {reasonSkipped || message || "This method was not required for the current query type."}
                </p>
              </div>
            </div>
          )}

          {/* Description Section */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">
              Theoretical Foundation & Description
            </h4>
            <p className="text-xs text-slate-300 bg-slate-900/60 border border-slate-800 rounded-lg p-3 leading-relaxed">
              {message}
            </p>
          </div>

          {/* Execution Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
              <span className="text-slate-400">Execution Duration:</span>
              <p className="text-sm font-bold text-cyan-400 mt-1">
                {duration !== null && duration !== undefined ? `${duration.toFixed(2)} ms` : "N/A"}
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
              <span className="text-slate-400">Execution Phase:</span>
              <p className="text-sm font-bold text-slate-200 mt-1">
                {isEvent ? item.stage : item.type.toUpperCase()}
              </p>
            </div>
          </div>

          {/* Input & Output Information */}
          {(inputInfo || outputInfo) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
              {inputInfo && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
                  <span className="text-slate-400">Input Data:</span>
                  <p className="text-slate-200 mt-1">{inputInfo}</p>
                </div>
              )}
              {outputInfo && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3">
                  <span className="text-slate-400">Output Data:</span>
                  <p className="text-emerald-300 mt-1">{outputInfo}</p>
                </div>
              )}
            </div>
          )}

          {/* Detailed JSON Payload */}
          {details && Object.keys(details).length > 0 && (
            <div className="space-y-1.5">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Code className="h-3.5 w-3.5 text-cyan-400" />
                Raw Execution Payload & Internal State
              </h4>
              <pre className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-cyan-300 overflow-x-auto max-h-48">
                {JSON.stringify(details, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-900/80 border-t border-slate-800 px-6 py-3 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs px-4 py-2 rounded-lg transition-colors font-mono"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
