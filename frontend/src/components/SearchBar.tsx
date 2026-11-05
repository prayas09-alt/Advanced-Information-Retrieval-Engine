import React, { useState } from "react";
import { Search, X, SlidersHorizontal, Sparkles, HelpCircle, Loader2 } from "lucide-react";
import { SpellingSuggestion } from "../types/ir";

interface SearchBarProps {
  onSearch: (params: {
    query: string;
    mode: string;
    case_sensitive: boolean;
    remove_stopwords: boolean;
    apply_stemming: boolean;
    enable_query_expansion: boolean;
    enable_zone_weighting: boolean;
    enable_cluster_pruning: boolean;
    enable_lsi: boolean;
  }) => void;
  searching: boolean;
  spellingSuggestions: SpellingSuggestion[];
  onApplySpellingSuggestion: (correctedQuery: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  searching,
  spellingSuggestions,
  onApplySpellingSuggestion,
}) => {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<string>("auto");
  const [showOptions, setShowOptions] = useState(false);

  // Advanced IR Options State
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [removeStopwords, setRemoveStopwords] = useState(true);
  const [applyStemming, setApplyStemming] = useState(true);
  const [enableQueryExpansion, setEnableQueryExpansion] = useState(false);
  const [enableZoneWeighting, setEnableZoneWeighting] = useState(true);
  const [enableClusterPruning, setEnableClusterPruning] = useState(false);
  const [enableLsi, setEnableLsi] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSearch({
      query: query.trim(),
      mode,
      case_sensitive: caseSensitive,
      remove_stopwords: removeStopwords,
      apply_stemming: applyStemming,
      enable_query_expansion: enableQueryExpansion,
      enable_zone_weighting: enableZoneWeighting,
      enable_cluster_pruning: enableClusterPruning,
      enable_lsi: enableLsi,
    });
  };

  const handleClear = () => {
    setQuery("");
  };

  const setExampleQuery = (example: string) => {
    setQuery(example);
    onSearch({
      query: example,
      mode,
      case_sensitive: caseSensitive,
      remove_stopwords: removeStopwords,
      apply_stemming: applyStemming,
      enable_query_expansion: enableQueryExpansion,
      enable_zone_weighting: enableZoneWeighting,
      enable_cluster_pruning: enableClusterPruning,
      enable_lsi: enableLsi,
    });
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl">
      <form onSubmit={handleSubmit}>
        {/* Main Search Input Group */}
        <div className="relative flex items-center">
          <div className="absolute left-4 pointer-events-none text-slate-400">
            <Search className="h-5 w-5" />
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter word, phrase ('...'), boolean (AND/OR/NOT), proximity (NEAR/k), or wildcard (*)..."
            className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-cyan-500 rounded-xl py-3.5 pl-12 pr-28 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/20 font-mono transition-all"
          />

          <div className="absolute right-2.5 flex items-center gap-1.5">
            {query && (
              <button
                type="button"
                onClick={handleClear}
                className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
                title="Clear search"
              >
                <X className="h-4 w-4" />
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowOptions(!showOptions)}
              className={`p-2 rounded-lg border transition-colors ${
                showOptions
                  ? "bg-cyan-950 text-cyan-400 border-cyan-800"
                  : "bg-slate-800 text-slate-400 hover:text-slate-200 border-slate-700"
              }`}
              title="IR Pipeline Settings"
            >
              <SlidersHorizontal className="h-4 w-4" />
            </button>

            <button
              type="submit"
              disabled={searching || !query.trim()}
              className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-medium text-xs px-4 py-2.5 rounded-lg transition-all flex items-center gap-1.5 shadow-md shadow-cyan-600/20"
            >
              {searching ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-3.5 w-3.5" />
                  Search
                </>
              )}
            </button>
          </div>
        </div>

        {/* Spelling Correction Banner */}
        {spellingSuggestions.length > 0 && (
          <div className="mt-3 bg-amber-950/30 border border-amber-800/60 rounded-lg px-3.5 py-2 flex items-center justify-between text-xs text-amber-300">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-400 shrink-0" />
              <span>
                Did you mean:{" "}
                {spellingSuggestions.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      const newQ = query.replace(new RegExp(`\\b${s.original}\\b`, "i"), s.suggested);
                      setQuery(newQ);
                      onApplySpellingSuggestion(newQ);
                    }}
                    className="font-bold underline text-cyan-300 hover:text-cyan-200 mr-2"
                  >
                    "{s.suggested}"
                  </button>
                ))}
                ?
              </span>
            </div>
            <span className="text-[10px] text-amber-400/70 font-mono">
              Levenshtein & Soundex
            </span>
          </div>
        )}

        {/* Advanced IR Parameters Drawer */}
        {showOptions && (
          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80">
            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={caseSensitive}
                onChange={(e) => setCaseSensitive(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span>Case Sensitive Match (Skip Folding)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={removeStopwords}
                onChange={(e) => setRemoveStopwords(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span>Stop Word Filtering (179 words)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={applyStemming}
                onChange={(e) => setApplyStemming(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span>Porter Stemming Normalization</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={enableZoneWeighting}
                onChange={(e) => setEnableZoneWeighting(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span>Zone Weighting (Title Boost)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={enableQueryExpansion}
                onChange={(e) => setEnableQueryExpansion(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span className="text-cyan-400 font-semibold">Rocchio PRF Expansion (M45)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={enableLsi}
                onChange={(e) => setEnableLsi(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span>Latent Semantic Indexing (LSI)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-slate-100">
              <input
                type="checkbox"
                checked={enableClusterPruning}
                onChange={(e) => setEnableClusterPruning(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-cyan-500 focus:ring-0"
              />
              <span>Cluster Pruning Top-K</span>
            </label>
          </div>
        )}

        {/* Query Syntax Helper Chips */}
        <div className="mt-3 flex flex-wrap items-center gap-1.5 text-xs text-slate-400">
          <span className="flex items-center gap-1 text-[11px] font-mono mr-1 text-slate-400">
            <HelpCircle className="h-3.5 w-3.5" /> Syntax Examples:
          </span>
          <button
            type="button"
            onClick={() => setExampleQuery("information retrieval")}
            className="bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 hover:text-white transition-colors"
          >
            Multi-word: information retrieval
          </button>
          <button
            type="button"
            onClick={() => setExampleQuery('"information retrieval"')}
            className="bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 hover:text-white transition-colors"
          >
            Phrase: "information retrieval"
          </button>
          <button
            type="button"
            onClick={() => setExampleQuery("inverted AND index NOT compression")}
            className="bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 hover:text-white transition-colors"
          >
            Boolean: AND / NOT
          </button>
          <button
            type="button"
            onClick={() => setExampleQuery("retriev*")}
            className="bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 hover:text-white transition-colors"
          >
            Wildcard: retriev*
          </button>
          <button
            type="button"
            onClick={() => setExampleQuery("vector NEAR/3 space")}
            className="bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 hover:text-white transition-colors"
          >
            Proximity: NEAR/3
          </button>
          <button
            type="button"
            onClick={() => setExampleQuery("retreival")}
            className="bg-slate-800/80 hover:bg-slate-700 border border-slate-700 px-2 py-0.5 rounded text-[11px] font-mono text-amber-300 hover:text-amber-200 transition-colors"
          >
            Typo Test: retreival
          </button>
        </div>
      </form>
    </div>
  );
};
