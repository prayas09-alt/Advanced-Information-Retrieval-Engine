export type MethodStatus = "PENDING" | "RUNNING" | "COMPLETED" | "SKIPPED" | "FAILED";
export type LogLevel = "INFO" | "SUCCESS" | "WARNING" | "ERROR" | "SKIPPED";

export interface ExecutionEvent {
  id: string;
  timestamp: string;
  stage: string;
  method_id?: number | null;
  method_name: string;
  status: MethodStatus;
  level: LogLevel;
  message: string;
  duration_ms?: number | null;
  details?: Record<string, any> | null;
}

export interface IRMethodState {
  id: number;
  name: string;
  category: string;
  type: string;
  description: string;
  status: MethodStatus;
  duration_ms: number;
  input_info?: string | null;
  output_info?: string | null;
  reason_skipped?: string | null;
  details?: Record<string, any> | null;
  last_run?: string | null;
}

export interface TermBreakdownItem {
  tf: number;
  idf: number;
  tfidf: number;
}

export interface SearchResultItem {
  doc_id: number;
  rank: number;
  cosine_score: number;
  tfidf_score: number;
  term_frequency: number;
  term_breakdown: Record<string, TermBreakdownItem>;
  zone: string;
  text: string;
  snippet: string;
  page: number;
  line_start: number;
  line_end: number;
  source_ref: string;
}

export interface SpellingSuggestion {
  original: string;
  suggested: string;
  candidates: Array<{
    candidate: string;
    levenshtein: number;
    weighted_edit: number;
    trigram_overlap: number;
    jaccard: number;
  }>;
}

export interface SearchHistoryItem {
  query: string;
  results_count: number;
  execution_time_ms: number;
  timestamp: string;
}

export interface SearchResponse {
  query: string;
  parsed_query: {
    raw_query: string;
    type: string;
    terms: string[];
    stems: string[];
    phrases: string[][];
    proximity?: [string, string, number] | null;
    boolean?: Record<string, string[]> | null;
    wildcards?: string[];
  };
  total_results: number;
  execution_time_ms: number;
  total_segments_searched: number;
  results: SearchResultItem[];
  spelling_suggestions: SpellingSuggestion[];
  expanded_query?: {
    original_stems: string[];
    expanded_stems: string[];
  } | null;
  lsi_results: Array<{ doc_id: number; lsi_score: number }>;
  search_history: SearchHistoryItem[];
}

export interface IndexStatus {
  indexed: boolean;
  metadata?: {
    filename: string;
    filepath: string;
    size_bytes: number;
    size_formatted: string;
    extension: string;
  };
  total_segments?: number;
  vocabulary_size?: number;
  total_term_doc_pairs?: number;
  index_build_time_ms?: number;
  compression_stats?: {
    raw_postings_bytes: number;
    variable_byte_bytes: number;
    vb_space_saving_pct: number;
    elias_sample_bits: number;
    dict_string_bytes: number;
    blocks_count: number;
    front_coding_blocks: number;
    total_compression_time_ms: number;
  };
  sample_terms?: string[];
}

export interface SampleFile {
  filename: string;
  filepath: string;
  extension: string;
  size_formatted: string;
}

export interface EvaluationItem {
  term: string;
  metrics: {
    precision_at_k: number;
    recall_at_k: number;
    f_measure: number;
    average_precision: number;
    r_precision: number;
    k: number;
    total_relevant: number;
    retrieved_relevant: number;
  };
}
