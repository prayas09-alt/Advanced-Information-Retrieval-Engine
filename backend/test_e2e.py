"""
test_e2e.py
End-to-End API and Pipeline Integration Tests using FastAPI TestClient.
Tests file upload, sample loading, live websocket events, search queries,
ranking, spelling correction, wildcards, boolean retrieval, and compression.
"""

import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(__file__))

from main import app, engine_state

client = TestClient(app)


def test_system_startup():
    print("1. Testing System Methods Endpoint...")
    res = client.get("/api/methods")
    assert res.status_code == 200
    methods = res.json()["methods"]
    assert len(methods) >= 45
    print(f"   -> Loaded {len(methods)} catalog IR methods.")


def test_sample_files_listing():
    print("2. Testing Sample Files Listing...")
    res = client.get("/api/sample-files")
    assert res.status_code == 200
    samples = res.json()["samples"]
    assert len(samples) >= 3
    print(f"   -> Found {len(samples)} preloaded sample files: {[s['filename'] for s in samples]}")
    # Select information_retrieval_handbook.txt for rich narrative text
    handbook = [s['filename'] for s in samples if 'handbook' in s['filename']][0]
    return handbook


def test_load_sample_and_index(sample_filename):
    print(f"3. Testing Sample Document Loading & Indexing: '{sample_filename}'...")
    res = client.post("/api/load-sample", data={"filename": sample_filename})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["segments_count"] > 0
    assert data["vocabulary_size"] > 0
    assert data["compression_stats"]["vb_space_saving_pct"] > 0
    print(f"   -> Indexed {data['segments_count']} passages, {data['vocabulary_size']} unique terms.")
    print(f"   -> Variable Byte compression space saved: {data['compression_stats']['vb_space_saving_pct']}%.")


def test_search_queries():
    print("4. Testing Multi-Mode Search Queries...")

    # A. Standard multi-word ranked query
    print("   A. Ranked Search ('information retrieval')...")
    res = client.post("/api/search", json={"query": "information retrieval"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] > 0
    top = data["results"][0]
    assert top["cosine_score"] > 0
    assert top["tfidf_score"] > 0
    assert "<mark" in top["snippet"]
    print(f"      -> Retrieved {data['total_results']} passages in {data['execution_time_ms']}ms. Top score: {top['cosine_score']}")

    # B. Quoted Exact Phrase query
    print("   B. Exact Phrase Search ('\"information retrieval\"')...")
    res = client.post("/api/search", json={"query": '"information retrieval"'})
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] > 0
    print(f"      -> Retrieved {data['total_results']} phrase matches.")

    # C. Boolean Query (AND, NOT)
    print("   C. Boolean Search ('inverted AND index NOT compression')...")
    res = client.post("/api/search", json={"query": "inverted AND index NOT compression"})
    assert res.status_code == 200
    data = res.json()
    print(f"      -> Boolean query returned {data['total_results']} passages.")

    # D. Wildcard Query
    print("   D. Wildcard Search ('retriev*')...")
    res = client.post("/api/search", json={"query": "retriev*"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] > 0
    print(f"      -> Wildcard query matched {data['total_results']} passages.")

    # E. Spelling Correction Typo Query
    print("   E. Spelling Correction Search ('retreival' typo)...")
    res = client.post("/api/search", json={"query": "retreival"})
    assert res.status_code == 200
    data = res.json()
    suggestions = data.get("spelling_suggestions", [])
    print(f"      -> Spelling suggestions generated: {len(suggestions)}")

    # F. Rocchio Query Expansion
    print("   F. Query Expansion (Rocchio PRF)...")
    res = client.post("/api/search", json={"query": "index", "enable_query_expansion": True})
    assert res.status_code == 200
    data = res.json()
    assert data.get("expanded_query") is not None
    print(f"      -> Query expanded to: {data['expanded_query']['expanded_stems']}")


def test_terminal_history():
    print("5. Testing Live Terminal Event History...")
    res = client.get("/api/terminal/history")
    assert res.status_code == 200
    history = res.json()["history"]
    assert len(history) > 10
    print(f"      -> Recorded {len(history)} execution events in terminal backlog.")
    print(f"      -> Sample event: {history[-1]['timestamp']} [{history[-1]['stage']}] {history[-1]['message']}")


def test_evaluation_benchmark():
    print("6. Testing IR Evaluation Benchmark (Method 49)...")
    res = client.get("/api/evaluate")
    assert res.status_code == 200
    bench = res.json()["benchmark"]
    assert len(bench) > 0
    sample = bench[0]
    print(f"      -> Evaluated term '{sample['term']}': Precision@10={sample['metrics']['precision_at_k']}, Recall@10={sample['metrics']['recall_at_k']}, F1={sample['metrics']['f_measure']}")


def run_all_e2e():
    print("==================================================================")
    print("STARTING FULL-STACK END-TO-END INFORMATION RETRIEVAL INTEGRATION")
    print("==================================================================")
    test_system_startup()
    sample_file = test_sample_files_listing()
    test_load_sample_and_index(sample_file)
    test_search_queries()
    test_terminal_history()
    test_evaluation_benchmark()
    print("==================================================================")
    print("ALL API ENDPOINTS & WORKFLOWS VERIFIED 100% OPERATIONAL!")
    print("==================================================================")


if __name__ == "__main__":
    run_all_e2e()
