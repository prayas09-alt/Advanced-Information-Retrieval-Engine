import React, { useState } from "react";
import { X, CheckCircle2, Play, Award, BarChart3, Loader2 } from "lucide-react";
import { api } from "../services/api";
import { EvaluationItem } from "../types/ir";

interface EvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EvaluationModal: React.FC<EvaluationModalProps> = ({ isOpen, onClose }) => {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<EvaluationItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleRunEvaluation = async () => {
    setRunning(true);
    setError(null);
    try {
      const data = await api.runEvaluation();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Evaluation failed. Make sure a document is uploaded first.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="bg-slate-900/80 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Award className="h-5 w-5 text-emerald-400" />
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Information Retrieval Evaluation Benchmark
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Method 49: Precision, Recall, F-measure, MAP, and R-Precision
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Evaluates retrieval quality against ground truth postings across multi-document terms.
                Computes Precision@10, Recall@10, F1 Harmonic Mean, Average Precision (AP), and R-Precision.
              </p>
            </div>

            <button
              onClick={handleRunEvaluation}
              disabled={running}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium text-xs px-4 py-2.5 rounded-lg transition-all flex items-center gap-2 font-mono shrink-0 shadow-lg shadow-emerald-600/20"
            >
              {running ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Evaluating...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Run Benchmark
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="bg-red-950/40 border border-red-800 rounded-lg p-3 text-xs text-red-300">
              {error}
            </div>
          )}

          {/* Results Table */}
          {results.length > 0 && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                Benchmark Results by Query Term
              </h4>

              <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400">
                      <th className="p-3">Query Term</th>
                      <th className="p-3">Precision@10</th>
                      <th className="p-3">Recall@10</th>
                      <th className="p-3">F-measure (F1)</th>
                      <th className="p-3">Avg Precision (AP)</th>
                      <th className="p-3">R-Precision</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-200">
                    {results.map((res, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="p-3 font-bold text-cyan-400">{res.term}</td>
                        <td className="p-3">{(res.metrics.precision_at_k * 100).toFixed(1)}%</td>
                        <td className="p-3 text-emerald-400 font-semibold">
                          {(res.metrics.recall_at_k * 100).toFixed(1)}%
                        </td>
                        <td className="p-3">{(res.metrics.f_measure * 100).toFixed(1)}%</td>
                        <td className="p-3 text-purple-400 font-semibold">
                          {(res.metrics.average_precision * 100).toFixed(1)}%
                        </td>
                        <td className="p-3">{(res.metrics.r_precision * 100).toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Summary Average Card */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 grid grid-cols-3 gap-3 text-center font-mono">
                <div>
                  <span className="text-[11px] text-slate-400">Mean Average Precision (MAP)</span>
                  <p className="text-xl font-bold text-cyan-400 mt-1">
                    {(
                      (results.reduce((acc, r) => acc + r.metrics.average_precision, 0) /
                        results.length) *
                      100
                    ).toFixed(1)}
                    %
                  </p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400">Average Recall@10</span>
                  <p className="text-xl font-bold text-emerald-400 mt-1">
                    {(
                      (results.reduce((acc, r) => acc + r.metrics.recall_at_k, 0) / results.length) *
                      100
                    ).toFixed(1)}
                    %
                  </p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400">Average F1-Measure</span>
                  <p className="text-xl font-bold text-purple-400 mt-1">
                    {(
                      (results.reduce((acc, r) => acc + r.metrics.f_measure, 0) / results.length) *
                      100
                    ).toFixed(1)}
                    %
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-900/80 border-t border-slate-800 px-6 py-3 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs px-4 py-2 rounded-lg transition-colors font-mono"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
