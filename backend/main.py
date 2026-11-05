"""
main.py
FastAPI application for Advanced Information Retrieval Search Engine.
Provides REST APIs, Server-Sent Events (SSE), and WebSockets for real-time Live Terminal updates.
"""

import os
import re
import time
import asyncio
from typing import List, Dict, Any, Optional, Set
from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from execution_logger import logger, ALL_METHODS_METADATA
from file_handler import FileHandler
from text_extractor import TextExtractor, TextSegment
from preprocessing import PreprocessingPipeline, stemmer, STANDARD_STOPWORDS
from indexer import Indexer, IndexBundle
from compression import CompressionBenchmark
from query_processor import QueryProcessor, ParsedQuery
from wildcard_search import WildcardEngine
from spelling_correction import SpellingCorrector
from boolean_retrieval import BooleanSearchEngine
from ranking import RankedRetrievalEngine, ScoredResult
from query_expansion import RocchioRelevanceFeedback
from advanced_ir import LatentSemanticIndexing, ClusterPruning, ZoneWeighting
from evaluation import IREvaluator

app = FastAPI(
    title="Advanced Information Retrieval Search Engine API",
    description="Full-stack IR Search Engine implementing 45+ Information Retrieval algorithms with real-time execution streaming.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Engine State
class GlobalEngineState:
    def __init__(self):
        self.file_metadata: Optional[Dict[str, Any]] = None
        self.segments: List[TextSegment] = []
        self.index_bundle: Optional[IndexBundle] = None
        self.ranked_engine: Optional[RankedRetrievalEngine] = None
        self.wildcard_engine: Optional[WildcardEngine] = None
        self.spelling_corrector: Optional[SpellingCorrector] = None
        self.boolean_engine: Optional[BooleanSearchEngine] = None
        self.lsi_engine: Optional[LatentSemanticIndexing] = None
        self.cluster_engine: Optional[ClusterPruning] = None
        self.compression_stats: Optional[Dict[str, Any]] = None
        self.zone_map: Dict[int, str] = {}
        self.search_history: List[Dict[str, Any]] = []


engine_state = GlobalEngineState()


class SearchRequest(BaseModel):
    query: str
    mode: str = "auto"  # 'auto', 'ranked', 'phrase', 'boolean', 'wildcard', 'proximity'
    top_k: int = 15
    case_sensitive: bool = False
    remove_stopwords: bool = True
    apply_stemming: bool = True
    enable_query_expansion: bool = False
    enable_zone_weighting: bool = True
    enable_cluster_pruning: bool = False
    enable_lsi: bool = False


@app.get("/")
async def root():
    return {
        "status": "online",
        "name": "Argus Information Retrieval Search Engine",
        "docs_url": "/docs",
        "methods_count": len(ALL_METHODS_METADATA)
    }


@app.on_event("startup")
async def startup_event():
    logger.log(
        stage="SYSTEM",
        method_id=None,
        method_name="Search Engine Core",
        status="COMPLETED",
        level="SUCCESS",
        message="Search Engine Core initialized. Ready to index documents.",
        details={"supported_formats": ["TXT", "PDF", "DOCX", "CSV"], "total_methods": len(ALL_METHODS_METADATA)}
    )
    # Ensure sample data is generated on startup
    FileHandler.get_sample_files()


# -------------------------------------------------------------
# Streaming & Terminal Endpoints
# -------------------------------------------------------------

@app.websocket("/ws/execution")
async def websocket_execution(websocket: WebSocket):
    """WebSocket endpoint for real-time live terminal execution updates."""
    await websocket.accept()
    queue = logger.subscribe()
    try:
        # Send initial backlog of recent history
        for evt in logger.get_history()[-40:]:
            await websocket.send_json(evt.dict())

        while True:
            evt = await queue.get()
            await websocket.send_json(evt.dict())
    except WebSocketDisconnect:
        pass
    finally:
        logger.unsubscribe(queue)


@app.get("/api/stream/events")
async def sse_execution():
    """Server-Sent Events fallback endpoint for streaming live terminal updates."""
    async def event_generator():
        queue = logger.subscribe()
        try:
            for evt in logger.get_history()[-20:]:
                yield f"data: {evt.json()}\n\n"
            while True:
                evt = await queue.get()
                yield f"data: {evt.json()}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            logger.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/terminal/history")
async def get_terminal_history():
    return {"history": [e.dict() for e in logger.get_history()]}


@app.post("/api/terminal/clear")
async def clear_terminal():
    logger.clear_history()
    return {"status": "cleared"}


# -------------------------------------------------------------
# File Upload & Indexing Pipeline
# -------------------------------------------------------------

def _execute_indexing_pipeline(filepath: str, filename: str, metadata: Dict[str, Any]):
    """Executes Methods 1-23 on the uploaded document."""
    t_start = time.time()
    logger.reset_methods()

    logger.log(
        stage="FILE",
        method_id=None,
        method_name="File Upload System",
        status="COMPLETED",
        level="SUCCESS",
        message=f"Document '{filename}' ({metadata['size_formatted']}, {metadata['extension']}) loaded successfully.",
        details=metadata
    )

    # Method 1: Document Parsing
    t0 = time.time()
    logger.log(
        stage="PREPROCESSING",
        method_id=1,
        method_name="Document Parsing",
        status="RUNNING",
        message=f"Extracting structured text from {metadata['extension']} file '{filename}'.",
        input_info=f"{metadata['size_formatted']} file",
        output_info="Segmenting passages"
    )

    segments, extract_stats = TextExtractor.extract_and_segment(filepath, filename)
    dur_parse = (time.time() - t0) * 1000

    logger.log(
        stage="PREPROCESSING",
        method_id=1,
        method_name="Document Parsing",
        status="COMPLETED",
        duration_ms=dur_parse,
        message=f"Extracted {len(segments)} discrete document passages ({extract_stats.get('raw_characters', 0)} characters).",
        input_info=f"{metadata['extension']} source file",
        output_info=f"{len(segments)} segments partitioned",
        details=extract_stats
    )

    if not segments:
        raise HTTPException(status_code=400, detail="Document contains no extractable text.")

    # Methods 2-6: Preprocessing Pipeline
    processed_docs = PreprocessingPipeline.process_segments(
        segments=segments,
        apply_case_folding=True,
        remove_stopwords=True,
        apply_stemming=True
    )

    # Methods 7-16: Index Construction
    index_bundle = Indexer.build_all(processed_docs)

    # Methods 17-23: Index Optimization & Compression
    all_postings = [p.doc_ids() for p in index_bundle.inverted_index.index.values()]
    comp_stats = CompressionBenchmark.run_all(
        dictionary_terms=index_bundle.dictionary.terms(),
        all_postings=all_postings
    )

    # Build Query Structures
    vocab = index_bundle.dictionary.terms()
    raw_words = sorted(list({t.lower() for pdoc in processed_docs for t in pdoc.tokens if len(t) > 2}))
    wildcard_eng = WildcardEngine(vocab)
    spelling_eng = SpellingCorrector(raw_words if raw_words else vocab)
    boolean_eng = BooleanSearchEngine(
        inverted_index=index_bundle.inverted_index,
        dictionary=index_bundle.dictionary,
        all_doc_ids=[s.doc_id for s in segments]
    )
    ranked_eng = RankedRetrievalEngine(
        dictionary=index_bundle.dictionary,
        inverted_index=index_bundle.inverted_index,
        total_docs=len(segments)
    )
    lsi_eng = LatentSemanticIndexing(
        vsm=ranked_eng.vsm,
        dictionary=index_bundle.dictionary,
        total_docs=len(segments)
    )
    cluster_eng = ClusterPruning(
        vsm=ranked_eng.vsm,
        total_docs=len(segments)
    )

    # Save to global state
    engine_state.file_metadata = metadata
    engine_state.segments = segments
    engine_state.index_bundle = index_bundle
    engine_state.ranked_engine = ranked_eng
    engine_state.wildcard_engine = wildcard_eng
    engine_state.spelling_corrector = spelling_eng
    engine_state.boolean_engine = boolean_eng
    engine_state.lsi_engine = lsi_eng
    engine_state.cluster_engine = cluster_eng
    engine_state.compression_stats = comp_stats
    engine_state.zone_map = {s.doc_id: s.zone for s in segments}

    total_pipeline_time = (time.time() - t_start) * 1000
    logger.log(
        stage="SYSTEM",
        method_id=None,
        method_name="Indexing Pipeline",
        status="COMPLETED",
        level="SUCCESS",
        message=f"Document indexing pipeline completed in {total_pipeline_time:.1f}ms. {len(vocab)} unique terms indexed across {len(segments)} passages.",
        details={"total_time_ms": round(total_pipeline_time, 2)}
    )


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a user document and builds the complete IR index."""
    try:
        filepath, metadata = FileHandler.save_upload(file.file, file.filename)
        _execute_indexing_pipeline(filepath, file.filename, metadata)
        return {
            "status": "success",
            "metadata": metadata,
            "segments_count": len(engine_state.segments),
            "vocabulary_size": engine_state.index_bundle.vocab_size,
            "total_term_doc_pairs": engine_state.index_bundle.total_term_doc_pairs,
            "compression_stats": engine_state.compression_stats,
            "sample_vocabulary": engine_state.index_bundle.dictionary.terms()[:20]
        }
    except Exception as e:
        logger.log(
            stage="FILE",
            method_id=None,
            method_name="Upload Error",
            status="FAILED",
            level="ERROR",
            message=f"Upload failed: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/sample-files")
async def list_sample_files():
    """Lists preloaded sample files for instant testing."""
    return {"samples": FileHandler.get_sample_files()}


@app.post("/api/load-sample")
async def load_sample_file(filename: str = Form(...)):
    """Loads a pre-bundled sample file into the search engine."""
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", filename)
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="Sample file not found.")

    ext = os.path.splitext(filename)[1].lower()
    size = os.path.getsize(sample_path)
    metadata = {
        "filename": filename,
        "filepath": sample_path,
        "size_bytes": size,
        "size_formatted": FileHandler._format_size(size),
        "extension": ext[1:].upper()
    }

    _execute_indexing_pipeline(sample_path, filename, metadata)
    return {
        "status": "success",
        "metadata": metadata,
        "segments_count": len(engine_state.segments),
        "vocabulary_size": engine_state.index_bundle.vocab_size,
        "compression_stats": engine_state.compression_stats
    }


# -------------------------------------------------------------
# Search Pipeline
# -------------------------------------------------------------

def _highlight_snippet(text: str, search_terms: List[str], max_length: int = 240) -> str:
    """Creates a snippet with matching terms surrounded by <mark> tags."""
    if not text:
        return ""
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in search_terms) + r")\b", re.IGNORECASE)
    highlighted = pattern.sub(r"<mark class='bg-cyan-500/30 text-cyan-200 font-semibold px-1 rounded'>\1</mark>", text)
    if len(highlighted) > max_length:
        return highlighted[:max_length] + "..."
    return highlighted


@app.post("/api/search")
async def search_query(req: SearchRequest):
    """Executes search query across the uploaded document using relevant IR methods."""
    if not engine_state.index_bundle:
        raise HTTPException(status_code=400, detail="No document indexed. Please upload a file first.")

    t_start = time.time()
    logger.reset_query_methods()

    logger.log(
        stage="QUERY",
        method_id=None,
        method_name="Query Handler",
        status="RUNNING",
        level="INFO",
        message=f"Received search query: '{req.query}' (Mode: {req.mode}).",
        details=req.dict()
    )

    # 1. Query Parsing (Method 24) & Tokenization (Method 25)
    parsed = QueryProcessor.parse_query(
        query_str=req.query,
        case_fold=not req.case_sensitive,
        remove_stopwords=req.remove_stopwords,
        apply_stemming=req.apply_stemming
    )

    # 2. Spelling Correction (Methods 29-32)
    spelling_suggestions = []
    corrected_terms = []
    for term in parsed.terms:
        best_cand, cands = engine_state.spelling_corrector.correct_term(term)
        if best_cand and best_cand != term:
            spelling_suggestions.append({"original": term, "suggested": best_cand, "candidates": cands})
            corrected_terms.append(best_cand)
        else:
            corrected_terms.append(term)

    # 3. Wildcard Resolution (Methods 26-28)
    expanded_wildcards = []
    if parsed.wildcard_patterns:
        for pat in parsed.wildcard_patterns:
            matches = engine_state.wildcard_engine.execute_wildcard(pat)
            expanded_wildcards.extend([stemmer.stem(m) for m in matches])
    else:
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=26,
            method_name="Wildcard Query Processing",
            status="SKIPPED",
            message="Wildcard search skipped: query contains no '*' wildcard character.",
            reason_skipped="No wildcard pattern detected"
        )
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=27,
            method_name="Permuterm Index",
            status="SKIPPED",
            message="Permuterm lookup skipped (query is not a wildcard query).",
            reason_skipped="No wildcard pattern detected"
        )
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=28,
            method_name="Bigram / N-gram Processing",
            status="SKIPPED",
            message="Bigram filtering skipped (no wildcard pattern).",
            reason_skipped="No wildcard pattern detected"
        )

    # 4. Determine Active Search Mode and Candidates
    filter_doc_ids: Optional[Set[int]] = None

    # Exact Phrase Matching (Method 33)
    if parsed.phrases:
        matching_phrase_docs = set()
        for p_stems in parsed.phrases:
            docs = QueryProcessor.match_phrase(
                phrase_stems=p_stems,
                positional_index=engine_state.index_bundle.positional_index,
                biword_index=engine_state.index_bundle.biword_index
            )
            matching_phrase_docs.update(docs)
        filter_doc_ids = matching_phrase_docs
    else:
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=33,
            method_name="Phrase Query Processing",
            status="SKIPPED",
            message="Phrase query processing skipped: query does not contain quoted phrases.",
            reason_skipped="No quoted phrases in query"
        )

    # Proximity Search (Method 34)
    if parsed.proximity_params:
        t1, t2, k = parsed.proximity_params
        prox_docs = QueryProcessor.match_proximity(
            term1=t1,
            term2=t2,
            k=k,
            positional_index=engine_state.index_bundle.positional_index
        )
        filter_doc_ids = set(prox_docs)
    else:
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=34,
            method_name="Proximity Search",
            status="SKIPPED",
            message="Proximity search skipped: query does not contain 'NEAR/k' operator.",
            reason_skipped="No NEAR operator specified"
        )

    # Boolean Retrieval (Methods 35-37)
    if parsed.boolean_params:
        b_docs = engine_state.boolean_engine.execute_complex_boolean(
            and_terms=parsed.boolean_params.get("AND", []),
            or_terms=parsed.boolean_params.get("OR", []),
            not_terms=parsed.boolean_params.get("NOT", [])
        )
        filter_doc_ids = set(b_docs)
    else:
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=35,
            method_name="Boolean Retrieval",
            status="SKIPPED",
            message="Boolean retrieval skipped: query does not specify Boolean logical operators (AND/OR/NOT).",
            reason_skipped="Standard ranked query mode active"
        )
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=36,
            method_name="Postings List Intersection",
            status="SKIPPED",
            message="Postings intersection skipped (using accumulator-based vector scoring).",
            reason_skipped="Conjunctive boolean logic not triggered"
        )
        logger.log(
            stage="QUERY_PROCESSING",
            method_id=37,
            method_name="Query Optimization",
            status="SKIPPED",
            message="Boolean term ordering optimization skipped.",
            reason_skipped="Conjunctive boolean logic not triggered"
        )

    # Combine query stems (original + wildcard expansions)
    active_query_stems = list(parsed.stems) + expanded_wildcards
    if not active_query_stems and parsed.phrases:
        active_query_stems = [s for p in parsed.phrases for s in p]

    # Cluster Pruning (Method 47) - optional acceleration
    if req.enable_cluster_pruning:
        q_weights, q_norm = engine_state.ranked_engine.vsm.create_query_vector(active_query_stems)
        _, cluster_followers = engine_state.cluster_engine.prune_and_search(q_weights, q_norm)
        if filter_doc_ids is not None:
            filter_doc_ids = filter_doc_ids.intersection(set(cluster_followers))
        else:
            filter_doc_ids = set(cluster_followers)
    else:
        logger.log(
            stage="ADVANCED_IR",
            method_id=47,
            method_name="Cluster Pruning",
            status="SKIPPED",
            message="Cluster pruning skipped: full collection Top-K evaluation enabled.",
            reason_skipped="Exact full collection ranking chosen"
        )

    # 5. Ranked Retrieval (Methods 38-44)
    zone_weights = engine_state.zone_map if req.enable_zone_weighting else None
    ranked_results: List[ScoredResult] = engine_state.ranked_engine.rank_query(
        query_stems=active_query_stems,
        top_k=req.top_k,
        filter_doc_ids=filter_doc_ids,
        zone_weights=zone_weights
    )

    # 6. Query Expansion & Pseudo-Relevance Feedback (Method 45)
    expanded_query_info = None
    if req.enable_query_expansion and ranked_results:
        top_ids = [r.doc_id for r in ranked_results[:3]]
        expanded_stems, _ = RocchioRelevanceFeedback.expand_query_prf(
            original_query_stems=active_query_stems,
            top_ranked_doc_ids=top_ids,
            vsm=engine_state.ranked_engine.vsm,
            dictionary=engine_state.index_bundle.dictionary,
            num_expansion_terms=3
        )
        expanded_query_info = {
            "original_stems": active_query_stems,
            "expanded_stems": expanded_stems
        }
        # Re-rank with expanded query
        ranked_results = engine_state.ranked_engine.rank_query(
            query_stems=expanded_stems,
            top_k=req.top_k,
            filter_doc_ids=filter_doc_ids,
            zone_weights=zone_weights
        )
    else:
        logger.log(
            stage="QUERY_EXPANSION",
            method_id=45,
            method_name="Query Expansion & Relevance Feedback",
            status="SKIPPED",
            message="Query expansion skipped: toggle is off in search options.",
            reason_skipped="Query expansion not requested"
        )

    # 7. Optional LSI Matching (Method 46)
    lsi_results = []
    if req.enable_lsi:
        lsi_matches = engine_state.lsi_engine.search_lsi(active_query_stems, top_k=5)
        lsi_results = [{"doc_id": d, "lsi_score": round(s, 4)} for d, s in lsi_matches]
    else:
        logger.log(
            stage="ADVANCED_IR",
            method_id=46,
            method_name="Latent Semantic Indexing (LSI)",
            status="SKIPPED",
            message="LSI semantic projection skipped (Vector Space Cosine ranking active).",
            reason_skipped="LSI option not enabled"
        )

    # Format Search Results
    formatted_results = []
    highlight_terms = list(parsed.terms)
    for sr in ranked_results:
        seg = engine_state.segments[sr.doc_id]
        snippet = _highlight_snippet(seg.text, highlight_terms)
        formatted_results.append({
            "doc_id": sr.doc_id,
            "rank": sr.rank,
            "cosine_score": sr.cosine_score,
            "tfidf_score": sr.tfidf_score,
            "term_frequency": sr.term_frequency,
            "term_breakdown": sr.term_breakdown,
            "zone": sr.zone,
            "text": seg.text,
            "snippet": snippet,
            "page": seg.page,
            "line_start": seg.line_start,
            "line_end": seg.line_end,
            "source_ref": seg.source_ref
        })

    total_search_time_ms = round((time.time() - t_start) * 1000, 2)
    logger.log(
        stage="COMPLETE",
        method_id=None,
        method_name="Search Pipeline",
        status="COMPLETED",
        level="SUCCESS",
        message=f"Search completed in {total_search_time_ms}ms. Retrieved {len(formatted_results)} matching passages.",
        details={"total_time_ms": total_search_time_ms, "results_count": len(formatted_results)}
    )

    # Save to search history
    history_entry = {
        "query": req.query,
        "results_count": len(formatted_results),
        "execution_time_ms": total_search_time_ms,
        "timestamp": time.strftime("%H:%M:%S")
    }
    engine_state.search_history.insert(0, history_entry)
    if len(engine_state.search_history) > 30:
        engine_state.search_history.pop()

    return {
        "query": req.query,
        "parsed_query": parsed.to_dict(),
        "total_results": len(formatted_results),
        "execution_time_ms": total_search_time_ms,
        "total_segments_searched": len(engine_state.segments),
        "results": formatted_results,
        "spelling_suggestions": spelling_suggestions,
        "expanded_query": expanded_query_info,
        "lsi_results": lsi_results,
        "search_history": engine_state.search_history
    }


# -------------------------------------------------------------
# Methods & Analytics Endpoints
# -------------------------------------------------------------

@app.get("/api/methods")
async def get_methods_status():
    """Returns catalog of all 45+ IR methods with real-time statuses and execution details."""
    return {"methods": logger.get_all_method_states()}


@app.get("/api/index/status")
async def get_index_status():
    """Returns active index statistics and document metadata."""
    if not engine_state.index_bundle:
        return {"indexed": False}

    return {
        "indexed": True,
        "metadata": engine_state.file_metadata,
        "total_segments": len(engine_state.segments),
        "vocabulary_size": engine_state.index_bundle.vocab_size,
        "total_term_doc_pairs": engine_state.index_bundle.total_term_doc_pairs,
        "index_build_time_ms": round(engine_state.index_bundle.build_time_ms, 2),
        "compression_stats": engine_state.compression_stats,
        "sample_terms": engine_state.index_bundle.dictionary.terms()[:30]
    }


@app.get("/api/evaluate")
async def evaluate_current_index():
    """Executes IR evaluation benchmark (Precision, Recall, F-measure, MAP, R-Precision)."""
    if not engine_state.segments:
        raise HTTPException(status_code=400, detail="No document indexed.")

    # Select top terms as ground truth test queries
    top_terms = [t for t in engine_state.index_bundle.dictionary.terms() if engine_state.index_bundle.dictionary.get_df(t) >= 2][:5]
    if not top_terms:
        top_terms = engine_state.index_bundle.dictionary.terms()[:3]

    eval_results = []
    for term in top_terms:
        plist = engine_state.index_bundle.inverted_index.get_postings(term)
        ground_truth_relevant = set(plist.doc_ids()) if plist else set()

        # Run ranked search
        results = engine_state.ranked_engine.rank_query([term], top_k=10)
        retrieved_ids = [r.doc_id for r in results]

        metrics = IREvaluator.evaluate_retrieval(
            retrieved_doc_ids=retrieved_ids,
            relevant_doc_ids=ground_truth_relevant,
            k=10
        )
        eval_results.append({"term": term, "metrics": metrics})

    return {"benchmark": eval_results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
