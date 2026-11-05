import { IndexStatus, SampleFile, SearchResponse, IRMethodState, EvaluationItem } from "../types/ir";

const API_BASE = "http://127.0.0.1:8000";

export const api = {
  async uploadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async getSampleFiles(): Promise<SampleFile[]> {
    const res = await fetch(`${API_BASE}/api/sample-files`);
    if (!res.ok) throw new Error("Failed to load sample files");
    const data = await res.json();
    return data.samples;
  },

  async loadSampleFile(filename: string): Promise<any> {
    const formData = new FormData();
    formData.append("filename", filename);
    const res = await fetch(`${API_BASE}/api/load-sample`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to load sample" }));
      throw new Error(err.detail || "Failed to load sample");
    }
    return res.json();
  },

  async search(params: {
    query: string;
    mode?: string;
    top_k?: number;
    case_sensitive?: boolean;
    remove_stopwords?: boolean;
    apply_stemming?: boolean;
    enable_query_expansion?: boolean;
    enable_zone_weighting?: boolean;
    enable_cluster_pruning?: boolean;
    enable_lsi?: boolean;
  }): Promise<SearchResponse> {
    const res = await fetch(`${API_BASE}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Search failed" }));
      throw new Error(err.detail || "Search failed");
    }
    return res.json();
  },

  async getIndexStatus(): Promise<IndexStatus> {
    const res = await fetch(`${API_BASE}/api/index/status`);
    if (!res.ok) throw new Error("Failed to fetch index status");
    return res.json();
  },

  async getMethods(): Promise<IRMethodState[]> {
    const res = await fetch(`${API_BASE}/api/methods`);
    if (!res.ok) throw new Error("Failed to fetch methods");
    const data = await res.json();
    return data.methods;
  },

  async clearTerminal(): Promise<void> {
    await fetch(`${API_BASE}/api/terminal/clear`, { method: "POST" });
  },

  async runEvaluation(): Promise<EvaluationItem[]> {
    const res = await fetch(`${API_BASE}/api/evaluate`);
    if (!res.ok) throw new Error("Failed to run evaluation");
    const data = await res.json();
    return data.benchmark;
  },
};
