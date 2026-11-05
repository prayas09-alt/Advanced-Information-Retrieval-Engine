import React, { useState, useEffect } from "react";
import { TopNav } from "./components/TopNav";
import { FileUpload } from "./components/FileUpload";
import { SearchBar } from "./components/SearchBar";
import { SearchResults } from "./components/SearchResults";
import { LiveTerminal } from "./components/LiveTerminal";
import { MethodDashboard } from "./components/MethodDashboard";
import { PipelineVisualizer } from "./components/PipelineVisualizer";
import { SearchAnalytics } from "./components/SearchAnalytics";
import { SearchHistory } from "./components/SearchHistory";
import { MethodDetailModal } from "./components/MethodDetailModal";
import { EvaluationModal } from "./components/EvaluationModal";
import { SampleFilesModal } from "./components/SampleFilesModal";
import { api } from "./services/api";
import { streamManager } from "./services/websocket";
import {
  IndexStatus,
  ExecutionEvent,
  IRMethodState,
  SearchResponse,
  SampleFile,
} from "./types/ir";

export const App: React.FC = () => {
  const [indexStatus, setIndexStatus] = useState<IndexStatus | null>(null);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [methods, setMethods] = useState<IRMethodState[]>([]);
  const [lastSearch, setLastSearch] = useState<SearchResponse | null>(null);
  const [sampleFiles, setSampleFiles] = useState<SampleFile[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [searching, setSearching] = useState<boolean>(false);
  const [activeView, setActiveView] = useState<"search" | "methods" | "terminal" | "analytics">("search");
  const [currentStage, setCurrentStage] = useState<string>("SYSTEM");

  // Modals state
  const [selectedItem, setSelectedItem] = useState<ExecutionEvent | IRMethodState | null>(null);
  const [isSampleModalOpen, setIsSampleModalOpen] = useState(false);
  const [isEvalModalOpen, setIsEvalModalOpen] = useState(false);

  useEffect(() => {
    // 1. Connect WebSocket / SSE stream
    streamManager.connect();
    const unsubEvent = streamManager.subscribe((event) => {
      setEvents((prev) => [...prev, event]);
      if (event.stage) {
        setCurrentStage(event.stage);
      }
      // Refresh methods state when events arrive
      if (event.method_id) {
        api.getMethods().then(setMethods).catch(() => {});
      }
    });

    const unsubStatus = streamManager.subscribeStatus((connected) => {
      setIsConnected(connected);
    });

    // 2. Fetch initial status and sample files
    api.getIndexStatus().then(setIndexStatus).catch(() => {});
    api.getMethods().then(setMethods).catch(() => {});
    api.getSampleFiles().then(setSampleFiles).catch(() => {});

    return () => {
      unsubEvent();
      unsubStatus();
      streamManager.disconnect();
    };
  }, []);

  const handleIndexingSuccess = (newStatus: IndexStatus) => {
    setIndexStatus(newStatus);
    api.getMethods().then(setMethods).catch(() => {});
  };

  const handleSearch = async (params: any) => {
    setSearching(true);
    try {
      const response = await api.search(params);
      setLastSearch(response);
      api.getMethods().then(setMethods).catch(() => {});
    } catch (err: any) {
      console.error("Search error:", err);
    } finally {
      setSearching(false);
    }
  };

  const handleClearTerminal = async () => {
    await api.clearTerminal();
    setEvents([]);
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navigation */}
      <TopNav
        indexStatus={indexStatus}
        isConnected={isConnected}
        activeView={activeView}
        setActiveView={setActiveView}
        onOpenSampleModal={() => setIsSampleModalOpen(true)}
        onOpenEvalModal={() => setIsEvalModalOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6 space-y-6">
        {/* Visual Pipeline Progress Bar */}
        <PipelineVisualizer
          currentStage={currentStage}
          hasDocument={Boolean(indexStatus?.indexed)}
          hasSearchResults={Boolean(lastSearch && lastSearch.results.length > 0)}
        />

        {/* View: Primary Search & Live Terminal Workspace */}
        {activeView === "search" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Upload, Search Bar & Results (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              <FileUpload
                indexStatus={indexStatus}
                onIndexingSuccess={handleIndexingSuccess}
                sampleFiles={sampleFiles}
              />

              {indexStatus?.indexed && (
                <>
                  <SearchBar
                    onSearch={handleSearch}
                    searching={searching}
                    spellingSuggestions={lastSearch?.spelling_suggestions || []}
                    onApplySpellingSuggestion={(corrected) =>
                      handleSearch({
                        query: corrected,
                        mode: "auto",
                        case_sensitive: false,
                        remove_stopwords: true,
                        apply_stemming: true,
                        enable_query_expansion: false,
                        enable_zone_weighting: true,
                        enable_cluster_pruning: false,
                        enable_lsi: false,
                      })
                    }
                  />

                  {lastSearch && (
                    <SearchResults
                      results={lastSearch.results}
                      totalResults={lastSearch.total_results}
                      executionTimeMs={lastSearch.execution_time_ms}
                      totalSegmentsSearched={lastSearch.total_segments_searched}
                      query={lastSearch.query}
                    />
                  )}

                  {lastSearch?.search_history && lastSearch.search_history.length > 0 && (
                    <SearchHistory
                      history={lastSearch.search_history}
                      onSelectQuery={(q) =>
                        handleSearch({
                          query: q,
                          mode: "auto",
                          case_sensitive: false,
                          remove_stopwords: true,
                          apply_stemming: true,
                          enable_query_expansion: false,
                          enable_zone_weighting: true,
                          enable_cluster_pruning: false,
                          enable_lsi: false,
                        })
                      }
                    />
                  )}
                </>
              )}
            </div>

            {/* Right Column: Live Execution Terminal (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              <LiveTerminal
                events={events}
                onClear={handleClearTerminal}
                onSelectEvent={(evt) => setSelectedItem(evt)}
              />

              {/* Compression Quick Widget */}
              {indexStatus?.compression_stats && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-xs font-mono">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="font-bold text-slate-200">Index Compression Efficiency</span>
                    <span className="text-cyan-400 font-bold">
                      {indexStatus.compression_stats.vb_space_saving_pct}% Saved
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] text-slate-400">
                    <div>Raw: {indexStatus.compression_stats.raw_postings_bytes} B</div>
                    <div className="text-emerald-400">VB: {indexStatus.compression_stats.variable_byte_bytes} B</div>
                    <div>Elias: {indexStatus.compression_stats.elias_sample_bits} bits</div>
                    <div>Dict String: {indexStatus.compression_stats.dict_string_bytes} B</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* View: All 45 IR Methods Dashboard */}
        {activeView === "methods" && (
          <MethodDashboard
            methods={methods}
            onSelectMethod={(method) => setSelectedItem(method)}
          />
        )}

        {/* View: Dedicated Live Terminal View */}
        {activeView === "terminal" && (
          <div className="space-y-4">
            <LiveTerminal
              events={events}
              onClear={handleClearTerminal}
              onSelectEvent={(evt) => setSelectedItem(evt)}
            />
          </div>
        )}

        {/* View: Search Analytics View */}
        {activeView === "analytics" && (
          <SearchAnalytics indexStatus={indexStatus} lastSearch={lastSearch} />
        )}
      </main>

      {/* Modals */}
      <MethodDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
      <EvaluationModal isOpen={isEvalModalOpen} onClose={() => setIsEvalModalOpen(false)} />
      <SampleFilesModal
        isOpen={isSampleModalOpen}
        onClose={() => setIsSampleModalOpen(false)}
        samples={sampleFiles}
        onSelectSample={async (fn) => {
          await api.loadSampleFile(fn);
          const st = await api.getIndexStatus();
          handleIndexingSuccess(st);
        }}
        loading={searching}
      />
    </div>
  );
};

export default App;
