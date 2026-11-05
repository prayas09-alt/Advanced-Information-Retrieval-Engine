import React, { useState } from "react";
import {
  FileText,
  Award,
  ChevronDown,
  ChevronUp,
  BarChart2,
  Sliders,
  Compass,
  MapPin,
  Percent,
} from "lucide-react";
import { SearchResultItem } from "../types/ir";

interface SearchResultsProps {
  results: SearchResultItem[];
  totalResults: number;
  executionTimeMs: number;
  totalSegmentsSearched: number;
  query: string;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  totalResults,
  executionTimeMs,
  totalSegmentsSearched,
  query,
}) => {
  const [sortBy, setSortBy] = useState<"cosine" | "frequency" | "position">("cosine");
  const [filterExact, setFilterExact] = useState(false);
  const [expandedCards, setExpandedCards] = useState<Record<number, boolean>>({});

  const toggleExpand = (docId: number) => {
    setExpandedCards((prev) => ({ ...prev, [docId]: !prev[docId] }));
  };

  // Sort and filter results
  let processedResults = [...results];

  if (filterExact) {
    const qLower = query.toLowerCase();
    processedResults = processedResults.filter((r) => r.text.toLowerCase().includes(qLower));
  }

  if (sortBy === "frequency") {
    processedResults.sort((a, b) => b.term_frequency - a.term_frequency);
  } else if (sortBy === "position") {
    processedResults.sort((a, b) => a.doc_id - b.doc_id);
  } else {
    // Cosine similarity
    processedResults.sort((a, b) => b.cosine_score - a.cosine_score);
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      {/* Results Header and Metrics */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Award className="h-5 w-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
              Matching Search Results
            </h3>
            <span className="bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs px-2 py-0.5 rounded-full font-mono">
              {totalResults} matches
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            Evaluated {totalSegmentsSearched} passages in {executionTimeMs.toFixed(1)}ms
          </p>
        </div>

        {/* Filters and Sorters */}
        <div className="flex items-center gap-2 text-xs">
          <label className="flex items-center gap-1.5 text-slate-300 hover:text-white cursor-pointer bg-slate-950 border border-slate-800 px-2.5 py-1 rounded-md">
            <input
              type="checkbox"
              checked={filterExact}
              onChange={(e) => setFilterExact(e.target.checked)}
              className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
            />
            <span>Exact match only</span>
          </label>

          <div className="flex items-center gap-1 bg-slate-950 border border-slate-800 px-2 py-1 rounded-md text-slate-300">
            <Sliders className="h-3.5 w-3.5 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="cosine">Sort by Relevance (Cosine)</option>
              <option value="frequency">Sort by Term Frequency</option>
              <option value="position">Sort by Document Position</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results List */}
      {processedResults.length === 0 ? (
        <div className="py-12 text-center text-slate-500">
          <FileText className="h-10 w-10 mx-auto mb-2 opacity-40" />
          <p className="text-sm font-medium">No matching passages found for "{query}".</p>
          <p className="text-xs text-slate-600 mt-1">
            Try broadening your search term, checking spelling suggestions, or toggling stemming/expansion.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {processedResults.map((item) => {
            const isExpanded = expandedCards[item.doc_id];

            return (
              <div
                key={item.doc_id}
                className="bg-slate-950/70 border border-slate-800/90 hover:border-slate-700 rounded-xl p-4 transition-all duration-200 hover:shadow-lg"
              >
                {/* Result Item Header */}
                <div className="flex items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold bg-cyan-950 text-cyan-300 border border-cyan-800 px-2 py-0.5 rounded">
                      Rank #{item.rank}
                    </span>

                    <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-slate-500" />
                      {item.source_ref}
                    </span>

                    {item.zone === "title" && (
                      <span className="text-[10px] bg-purple-950 text-purple-300 border border-purple-800 px-1.5 py-0.2 rounded font-mono font-semibold">
                        TITLE ZONE
                      </span>
                    )}
                  </div>

                  {/* Similarity Metrics Pills */}
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                      <Percent className="h-3 w-3 text-emerald-400" />
                      Cosine: {(item.cosine_score * 100).toFixed(1)}%
                    </span>

                    <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded">
                      TF-IDF: {item.tfidf_score.toFixed(3)}
                    </span>

                    <span className="bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded">
                      Occurrences: {item.term_frequency}
                    </span>
                  </div>
                </div>

                {/* Highlighted Snippet */}
                <div
                  className="text-sm text-slate-200 leading-relaxed font-sans"
                  dangerouslySetInnerHTML={{ __html: item.snippet || item.text }}
                />

                {/* Score Breakdown Expander */}
                <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between">
                  <button
                    onClick={() => toggleExpand(item.doc_id)}
                    className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors font-mono"
                  >
                    <BarChart2 className="h-3.5 w-3.5" />
                    {isExpanded ? "Hide TF / IDF Breakdown" : "View TF / IDF Breakdown"}
                    {isExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                  </button>

                  <span className="text-[11px] text-slate-400 font-mono">
                    Passage ID: doc_{item.doc_id}
                  </span>
                </div>

                {/* Expanded TF-IDF Details Table */}
                {isExpanded && (
                  <div className="mt-3 bg-slate-900 border border-slate-800 rounded-lg p-3 overflow-x-auto text-xs font-mono">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400">
                          <th className="pb-1.5 font-semibold">Query Term</th>
                          <th className="pb-1.5 font-semibold">Term Freq (TF)</th>
                          <th className="pb-1.5 font-semibold">Inverse Doc Freq (IDF)</th>
                          <th className="pb-1.5 font-semibold">TF-IDF Weight</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-300">
                        {Object.entries(item.term_breakdown).map(([term, scores]) => (
                          <tr key={term}>
                            <td className="py-1 text-cyan-300 font-semibold">{term}</td>
                            <td className="py-1">{scores.tf}</td>
                            <td className="py-1">{scores.idf.toFixed(3)}</td>
                            <td className="py-1 text-emerald-400 font-bold">{scores.tfidf.toFixed(3)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
