import React from "react";
import {
  BarChart3,
  Clock,
  Database,
  FileText,
  Binary,
  Layers,
  Percent,
  CheckCircle,
  TrendingUp,
} from "lucide-react";
import { IndexStatus, SearchResponse } from "../types/ir";

interface SearchAnalyticsProps {
  indexStatus: IndexStatus | null;
  lastSearch: SearchResponse | null;
}

export const SearchAnalytics: React.FC<SearchAnalyticsProps> = ({
  indexStatus,
  lastSearch,
}) => {
  const comp = indexStatus?.compression_stats;

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl space-y-5">
      <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
        <BarChart3 className="h-5 w-5 text-cyan-400" />
        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wide">
          Search Analytics & Compression Dashboard
        </h3>
      </div>

      {/* Main Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {/* Passages Extracted */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Total Passages</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-slate-100">
              {indexStatus?.total_segments || 0}
            </span>
            <span className="text-xs text-slate-500">units</span>
          </div>
        </div>

        {/* Unique Vocabulary Terms */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Unique Vocabulary</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-cyan-400">
              {indexStatus?.vocabulary_size || 0}
            </span>
            <span className="text-xs text-slate-500">stems</span>
          </div>
        </div>

        {/* Total Term-Doc Postings */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Indexed Postings Pairs</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-emerald-400">
              {indexStatus?.total_term_doc_pairs || 0}
            </span>
            <span className="text-xs text-slate-500">pairs</span>
          </div>
        </div>

        {/* Compression Space Saving */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">VB Compression Saving</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-purple-400">
              {comp?.vb_space_saving_pct || 0}%
            </span>
            <span className="text-xs text-slate-500">saved</span>
          </div>
        </div>

        {/* Index Construction Latency */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Index Build Latency</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-amber-400">
              {indexStatus?.index_build_time_ms || 0}
            </span>
            <span className="text-xs text-slate-500">ms</span>
          </div>
        </div>

        {/* Query Search Latency */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Last Query Latency</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-sky-400">
              {lastSearch?.execution_time_ms || 0}
            </span>
            <span className="text-xs text-slate-500">ms</span>
          </div>
        </div>

        {/* Matching Passages */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Matching Passages</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-emerald-300">
              {lastSearch?.total_results || 0}
            </span>
            <span className="text-xs text-slate-500">matches</span>
          </div>
        </div>

        {/* Corpus Raw Size */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between">
          <span className="text-[11px] font-mono text-slate-400">Uploaded File Size</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-slate-200">
              {indexStatus?.metadata?.size_formatted || "0 B"}
            </span>
          </div>
        </div>
      </div>

      {/* Compression Algorithms Benchmark Comparison */}
      {comp && (
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-3">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
            <Binary className="h-4 w-4 text-cyan-400" />
            Index Compression Benchmark (Methods 17 - 22)
          </h4>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono">
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Raw Postings (32-bit):</span>
              <p className="text-lg font-bold text-slate-200 mt-1">{comp.raw_postings_bytes} bytes</p>
              <span className="text-[10px] text-slate-500">Baseline uncompressed</span>
            </div>

            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Variable Byte (VB):</span>
              <p className="text-lg font-bold text-emerald-400 mt-1">{comp.variable_byte_bytes} bytes</p>
              <span className="text-[10px] text-emerald-400">{comp.vb_space_saving_pct}% size reduction</span>
            </div>

            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Elias Gamma Coding:</span>
              <p className="text-lg font-bold text-cyan-400 mt-1">{comp.elias_sample_bits} bits</p>
              <span className="text-[10px] text-slate-500">Unary length + binary offset</span>
            </div>

            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-slate-400">Dictionary-as-String:</span>
              <p className="text-lg font-bold text-purple-400 mt-1">{comp.dict_string_bytes} bytes</p>
              <span className="text-[10px] text-slate-500">{comp.blocks_count} blocks (k=4)</span>
            </div>
          </div>
        </div>
      )}

      {/* Vocabulary Distribution Sample */}
      {indexStatus?.sample_terms && indexStatus.sample_terms.length > 0 && (
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
          <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wide mb-3 flex items-center gap-2">
            <Database className="h-4 w-4 text-cyan-400" />
            Lexicon Sample (Indexed Stems)
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {indexStatus.sample_terms.map((term, idx) => (
              <span
                key={idx}
                className="text-xs font-mono bg-slate-900 text-slate-300 border border-slate-800 px-2.5 py-1 rounded-md"
              >
                {term}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
