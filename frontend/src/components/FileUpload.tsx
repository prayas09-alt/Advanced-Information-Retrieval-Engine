import React, { useState, useRef } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles, FolderOpen } from "lucide-react";
import { api } from "../services/api";
import { IndexStatus, SampleFile } from "../types/ir";

interface FileUploadProps {
  indexStatus: IndexStatus | null;
  onIndexingSuccess: (status: IndexStatus) => void;
  sampleFiles: SampleFile[];
}

export const FileUpload: React.FC<FileUploadProps> = ({
  indexStatus,
  onIndexingSuccess,
  sampleFiles,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processUpload(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processUpload(e.target.files[0]);
    }
  };

  const processUpload = async (file: File) => {
    setErrorMsg(null);
    setUploading(true);
    try {
      await api.uploadFile(file);
      const newStatus = await api.getIndexStatus();
      onIndexingSuccess(newStatus);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to process document.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleLoadSample = async (filename: string) => {
    setErrorMsg(null);
    setUploading(true);
    try {
      await api.loadSampleFile(filename);
      const newStatus = await api.getIndexStatus();
      onIndexingSuccess(newStatus);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load sample document.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Upload className="h-5 w-5 text-cyan-400" />
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
            File Upload & Indexing System
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
          Supported: TXT, PDF, DOCX, CSV
        </span>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? "border-cyan-400 bg-cyan-950/20 scale-[1.01]"
            : "border-slate-700/80 hover:border-slate-600 bg-slate-950/50 hover:bg-slate-950/80"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf,.docx,.doc,.csv"
          onChange={handleFileChange}
          className="hidden"
        />

        {uploading ? (
          <div className="flex flex-col items-center justify-center py-3">
            <Loader2 className="h-9 w-9 text-cyan-400 animate-spin mb-3" />
            <p className="text-sm font-medium text-slate-200">Executing IR Indexing Pipeline...</p>
            <p className="text-xs text-slate-400 mt-1">
              Extracting text → Tokenizing → Porter Stemming → Positional & Inverted Index → Compression
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-2">
            <div className="h-11 w-11 rounded-full bg-slate-800/80 flex items-center justify-center text-cyan-400 mb-3 border border-slate-700/60">
              <FolderOpen className="h-6 w-6" />
            </div>
            <p className="text-sm font-medium text-slate-200">
              Drag & drop document here, or <span className="text-cyan-400 font-semibold underline">browse file</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Plain text (.txt), PDF (.pdf), Word (.docx), or Structured CSV (.csv)
            </p>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {errorMsg && (
        <div className="mt-3 bg-red-950/40 border border-red-800/80 rounded-lg p-3 flex items-start gap-2.5 text-xs text-red-300">
          <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 shrink-0" />
          <div>
            <span className="font-semibold">Processing Error:</span> {errorMsg}
          </div>
        </div>
      )}

      {/* Active Indexed File Summary Card */}
      {indexStatus?.indexed && indexStatus.metadata && (
        <div className="mt-4 bg-slate-950/90 border border-slate-800 rounded-lg p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 font-bold text-xs">
              {indexStatus.metadata.extension}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-100">{indexStatus.metadata.filename}</span>
                <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.2 rounded font-mono flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3" /> INDEXED
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Size: {indexStatus.metadata.size_formatted} | Passages: {indexStatus.total_segments} | Vocabulary:{" "}
                {indexStatus.vocabulary_size} terms | Index Time: {indexStatus.index_build_time_ms}ms
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[11px] text-slate-400 font-mono">
              Compression:{" "}
              <span className="text-cyan-400 font-bold">
                {indexStatus.compression_stats?.vb_space_saving_pct || 0}% space saved
              </span>
            </span>
          </div>
        </div>
      )}

      {/* Quick Preloaded Sample Document Chips */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium text-slate-400 flex items-center gap-1 mr-1">
          <Sparkles className="h-3.5 w-3.5 text-amber-400" />
          One-Click Samples:
        </span>
        {sampleFiles.map((sf) => (
          <button
            key={sf.filename}
            disabled={uploading}
            onClick={() => handleLoadSample(sf.filename)}
            className="text-xs bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-300 hover:text-cyan-300 px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5 font-mono disabled:opacity-50"
          >
            <FileText className="h-3 w-3 text-cyan-400" />
            <span className="truncate max-w-[170px]">{sf.filename}</span>
            <span className="text-[10px] text-slate-400">({sf.extension})</span>
          </button>
        ))}
      </div>
    </div>
  );
};
