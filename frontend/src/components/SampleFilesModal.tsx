import React from "react";
import { X, FileText, CheckCircle, ArrowRight } from "lucide-react";
import { SampleFile } from "../types/ir";

interface SampleFilesModalProps {
  isOpen: boolean;
  onClose: () => void;
  samples: SampleFile[];
  onSelectSample: (filename: string) => void;
  loading: boolean;
}

export const SampleFilesModal: React.FC<SampleFilesModalProps> = ({
  isOpen,
  onClose,
  samples,
  onSelectSample,
  loading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl w-full max-w-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        {/* Header */}
        <div className="bg-slate-900/80 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <FileText className="h-5 w-5 text-cyan-400" />
            <div>
              <h3 className="text-base font-bold text-slate-100">Preloaded Sample Documents</h3>
              <p className="text-xs text-slate-400 font-mono">
                Click any document to index it and test all 45 IR algorithms
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
        <div className="p-6 overflow-y-auto space-y-3">
          {samples.map((sf) => (
            <div
              key={sf.filename}
              onClick={() => {
                if (!loading) {
                  onSelectSample(sf.filename);
                  onClose();
                }
              }}
              className="group bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/60 rounded-xl p-4 cursor-pointer transition-all flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 font-bold text-xs font-mono">
                  {sf.extension}
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors font-mono">
                    {sf.filename}
                  </h4>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">
                    Size: {sf.size_formatted} | Format: {sf.extension}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 group-hover:translate-x-1 transition-transform">
                <span>Load & Index</span>
                <ArrowRight className="h-4 w-4" />
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="bg-slate-900/80 border-t border-slate-800 px-6 py-3 flex justify-end">
          <button
            onClick={onClose}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs px-4 py-2 rounded-lg transition-colors font-mono"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
