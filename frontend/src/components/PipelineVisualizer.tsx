import React from "react";
import { Check, ArrowRight, Clock, FileUp, FileText, Binary, Search, Filter, BarChart3, Award } from "lucide-react";

interface PipelineVisualizerProps {
  currentStage: string;
  hasDocument: boolean;
  hasSearchResults: boolean;
}

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({
  currentStage,
  hasDocument,
  hasSearchResults,
}) => {
  const stages = [
    { id: "UPLOAD", label: "File Upload", icon: FileUp, completed: hasDocument },
    { id: "EXTRACTION", label: "Text Extraction", icon: FileText, completed: hasDocument },
    { id: "PREPROCESSING", label: "Preprocessing", icon: Binary, completed: hasDocument },
    { id: "INDEXING", label: "Index Construction", icon: Binary, completed: hasDocument },
    { id: "QUERY", label: "Query Parsing", icon: Search, completed: hasSearchResults },
    { id: "MATCHING", label: "Matching & Postings", icon: Filter, completed: hasSearchResults },
    { id: "RANKING", label: "Ranking (TF-IDF/Cosine)", icon: BarChart3, completed: hasSearchResults },
    { id: "RESULTS", label: "Results Generation", icon: Award, completed: hasSearchResults },
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-lg overflow-x-auto">
      <div className="flex items-center justify-between min-w-[780px] gap-2">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isActive = currentStage.toUpperCase() === stage.id;
          const isDone = stage.completed;

          return (
            <React.Fragment key={stage.id}>
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`h-9 w-9 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isActive
                      ? "bg-cyan-500 text-white ring-4 ring-cyan-500/30 scale-110 shadow-lg shadow-cyan-500/40"
                      : isDone
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-700/80"
                      : "bg-slate-800 text-slate-500 border border-slate-700"
                  }`}
                >
                  {isDone ? (
                    <Check className="h-4 w-4" />
                  ) : isActive ? (
                    <Clock className="h-4 w-4 animate-spin" />
                  ) : (
                    <Icon className="h-4 w-4" />
                  )}
                </div>

                <span
                  className={`text-[11px] font-mono mt-1.5 text-center leading-tight ${
                    isActive
                      ? "text-cyan-400 font-bold"
                      : isDone
                      ? "text-slate-300 font-medium"
                      : "text-slate-500"
                  }`}
                >
                  {stage.label}
                </span>
              </div>

              {idx < stages.length - 1 && (
                <ArrowRight
                  className={`h-3.5 w-3.5 shrink-0 -mt-4 transition-colors ${
                    isDone ? "text-emerald-500" : "text-slate-700"
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
