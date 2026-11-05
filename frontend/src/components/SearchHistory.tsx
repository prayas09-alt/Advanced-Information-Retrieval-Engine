import React from "react";
import { History, Search, Clock, ArrowRight } from "lucide-react";
import { SearchHistoryItem } from "../types/ir";

interface SearchHistoryProps {
  history: SearchHistoryItem[];
  onSelectQuery: (query: string) => void;
}

export const SearchHistory: React.FC<SearchHistoryProps> = ({
  history,
  onSelectQuery,
}) => {
  if (history.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-xl space-y-3">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
        <History className="h-4 w-4 text-cyan-400" />
        <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">
          Recent Search History
        </h3>
      </div>

      <div className="space-y-1.5 max-h-48 overflow-y-auto">
        {history.map((item, idx) => (
          <div
            key={idx}
            onClick={() => onSelectQuery(item.query)}
            className="group flex items-center justify-between p-2 rounded-lg bg-slate-950/60 hover:bg-slate-800/60 border border-slate-800/80 hover:border-slate-700 cursor-pointer transition-colors text-xs font-mono"
          >
            <div className="flex items-center gap-2 truncate">
              <Search className="h-3 w-3 text-slate-500 group-hover:text-cyan-400 transition-colors shrink-0" />
              <span className="text-slate-200 group-hover:text-cyan-300 transition-colors truncate">
                {item.query}
              </span>
            </div>

            <div className="flex items-center gap-2 text-[10px] text-slate-400 shrink-0">
              <span className="text-emerald-400">{item.results_count} results</span>
              <span>•</span>
              <span>{item.execution_time_ms.toFixed(0)}ms</span>
              <ArrowRight className="h-3 w-3 opacity-0 group-hover:opacity-100 text-cyan-400 transition-opacity" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
