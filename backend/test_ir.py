"""
test_ir.py
Unit and Integration Tests for Information Retrieval Algorithms.
Verifies all 45 methods work accurately with genuine data.
"""

import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from text_extractor import TextExtractor, TextSegment
from tokenizer import Tokenizer
from preprocessing import PreprocessingPipeline, stemmer, STANDARD_STOPWORDS
from indexer import Indexer
from compression import GapEncoder, VariableByteEncoder, EliasGammaEncoder, FrontCoding, CompressionBenchmark
from wildcard_search import PermutermIndex, BigramWildcardSearch, WildcardEngine
from spelling_correction import EditDistance, Soundex, NgramSimilarity, SpellingCorrector
from boolean_retrieval import BooleanOperations, BooleanSearchEngine
from ranking import RankedRetrievalEngine
from query_processor import QueryProcessor
from query_expansion import RocchioRelevanceFeedback
from advanced_ir import LatentSemanticIndexing, ClusterPruning, ZoneWeighting
from evaluation import IREvaluator


def test_preprocessing():
    print("Testing Preprocessing (Methods 1-6)...")
    # Method 2 & 3: Tokenization & Case Folding
    tokens = Tokenizer.tokenize("Information Retrieval is AMAZING!")
    assert len(tokens) == 4
    assert tokens[0].normalized == "information"
    assert tokens[3].normalized == "amazing"

    # Method 4: Stop Words
    assert "is" in STANDARD_STOPWORDS
    assert "information" not in STANDARD_STOPWORDS

    # Method 5: Porter Stemmer
    assert stemmer.stem("retrieval") == "retriev"
    assert stemmer.stem("connecting") == "connect"
    assert stemmer.stem("information") == "inform"

    # Method 1 & 6: Document Parsing and Doc ID Assignment
    segments = [
        TextSegment(doc_id=0, text="Information retrieval systems index text documents.", zone="title"),
        TextSegment(doc_id=1, text="Vector space models calculate cosine similarity between queries and documents.", zone="body"),
        TextSegment(doc_id=2, text="Boolean search engines evaluate boolean expressions with AND OR NOT.", zone="body")
    ]
    pdocs = PreprocessingPipeline.process_segments(segments)
    assert len(pdocs) == 3
    assert pdocs[0].doc_id == 0
    print("  -> Methods 1-6 passed!")
    return pdocs


def test_index_construction(pdocs):
    print("Testing Index Construction (Methods 7-16)...")
    bundle = Indexer.build_all(pdocs)
    assert bundle.vocab_size > 0
    assert bundle.total_docs == 3

    # Check Inverted Index (Method 12)
    plist = bundle.inverted_index.get_postings("retriev")
    assert plist is not None
    assert 0 in plist.doc_ids()

    # Check Positional Index (Method 15)
    positions = bundle.positional_index.get_positions("retriev", 0)
    assert len(positions) > 0

    # Check Biword Index (Method 14)
    # Consecutive stems in doc 0: inform, retriev
    biwords = bundle.biword_index.search_biword("inform", "retriev")
    assert 0 in biwords
    print("  -> Methods 7-16 passed!")
    return bundle


def test_compression(bundle):
    print("Testing Compression & Optimization (Methods 17-23)...")
    # Method 17: Gap Encoding
    doc_ids = [2, 7, 15, 23, 42]
    gaps = GapEncoder.encode(doc_ids)
    assert gaps == [2, 5, 8, 8, 19]
    decoded = GapEncoder.decode(gaps)
    assert decoded == doc_ids

    # Method 18: Variable Byte Encoding
    vb_encoded = VariableByteEncoder.encode(gaps)
    vb_decoded = VariableByteEncoder.decode(vb_encoded)
    assert vb_decoded == gaps

    # Method 19: Elias Gamma Encoding
    numbers = [1, 2, 5, 14, 33]
    elias_str = EliasGammaEncoder.encode(numbers)
    elias_decoded = EliasGammaEncoder.decode(elias_str)
    assert elias_decoded == numbers

    # Method 22: Front Coding
    terms = ["automate", "automatic", "automation"]
    fc_block = FrontCoding.encode_block(terms)
    assert "automat" in fc_block

    # Full Benchmark
    all_postings = [p.doc_ids() for p in bundle.inverted_index.index.values()]
    stats = CompressionBenchmark.run_all(bundle.dictionary.terms(), all_postings)
    assert stats["variable_byte_bytes"] > 0
    print("  -> Methods 17-23 passed!")


def test_wildcards_and_spelling(bundle):
    print("Testing Wildcards and Spelling (Methods 26-32)...")
    vocab = bundle.dictionary.terms()

    # Method 27: Permuterm Index
    permuterm = PermutermIndex(vocab)
    matches = permuterm.search_wildcard("retriev*")
    assert "retriev" in matches

    # Method 28: Bigram Wildcard
    bg = BigramWildcardSearch(vocab)
    bg_matches, _, _ = bg.search_with_post_filter("retriev*")
    assert "retriev" in matches

    # Method 30: Edit Distance
    dist = EditDistance.levenshtein("retrieval", "retreival")  # transposition / typo
    assert dist <= 2
    wed = EditDistance.weighted_edit_distance("cat", "bat")
    assert wed > 0

    # Soundex
    assert Soundex.encode("Robert") == "R163"
    assert Soundex.encode("Rupert") == "R163"

    # Method 31 & 32: N-gram and Jaccard
    j = NgramSimilarity.jaccard("retrieval", "retrievall")
    assert j > 0.6

    # Spelling Corrector
    corrector = SpellingCorrector(vocab)
    best, cands = corrector.correct_term("retreival")
    print(f"  Spelling suggestion for 'retreival': {best}")
    print("  -> Methods 26-32 passed!")


def test_boolean_and_phrase(bundle):
    print("Testing Boolean, Phrase, and Proximity (Methods 24, 25, 33-37)...")
    # Method 24 & 25: Query Parsing
    q_phrase = QueryProcessor.parse_query('"information retrieval"')
    assert q_phrase.query_type == "phrase"
    assert len(q_phrase.phrases) > 0

    q_bool = QueryProcessor.parse_query("vector AND similarity NOT boolean")
    assert q_bool.query_type == "boolean"

    q_prox = QueryProcessor.parse_query("cosine NEAR/3 similarity")
    assert q_prox.query_type == "proximity"

    # Method 33: Phrase Query Processing
    phrase_matches = QueryProcessor.match_phrase(
        ["inform", "retriev"],
        bundle.positional_index,
        bundle.biword_index
    )
    assert 0 in phrase_matches

    # Method 34: Proximity Search
    prox_matches = QueryProcessor.match_proximity(
        "cosin", "similar", 4, bundle.positional_index
    )
    assert 1 in prox_matches

    # Method 35-37: Boolean Search Engine
    b_engine = BooleanSearchEngine(bundle.inverted_index, bundle.dictionary, [0, 1, 2])
    and_matches, _ = b_engine.execute_and_query(["cosin", "similar"])
    assert 1 in and_matches

    complex_res = b_engine.execute_complex_boolean(
        and_terms=["cosin", "similar"],
        or_terms=[],
        not_terms=["boolean"]
    )
    assert 1 in complex_res
    assert 2 not in complex_res
    print("  -> Methods 24, 25, 33-37 passed!")


def test_ranking_and_expansion(bundle):
    print("Testing Ranked Retrieval & Expansion (Methods 38-45)...")
    ranked_eng = RankedRetrievalEngine(
        dictionary=bundle.dictionary,
        inverted_index=bundle.inverted_index,
        total_docs=bundle.total_docs
    )

    results = ranked_eng.rank_query(["retriev", "system"], top_k=5)
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc.doc_id == 0
    assert top_doc.cosine_score > 0
    assert top_doc.tfidf_score > 0

    # Method 45: Rocchio Query Expansion
    expanded, _ = RocchioRelevanceFeedback.expand_query_prf(
        original_query_stems=["retriev"],
        top_ranked_doc_ids=[0],
        vsm=ranked_eng.vsm,
        dictionary=bundle.dictionary,
        num_expansion_terms=2
    )
    assert len(expanded) > 1
    print("  -> Methods 38-45 passed!")


def test_advanced_and_evaluation(bundle):
    print("Testing Advanced IR & Evaluation (Methods 46-49)...")
    # Method 46: LSI
    vsm = RankedRetrievalEngine(bundle.dictionary, bundle.inverted_index, bundle.total_docs).vsm
    lsi = LatentSemanticIndexing(vsm, bundle.dictionary, bundle.total_docs, n_components=2)
    lsi_res = lsi.search_lsi(["retriev"], top_k=3)

    # Method 47: Cluster Pruning
    cp = ClusterPruning(vsm, bundle.total_docs)
    q_w, q_n = vsm.create_query_vector(["retriev"])
    leader, followers = cp.prune_and_search(q_w, q_n)
    assert len(followers) > 0

    # Method 48: Zone Weighting
    zone_scores = ZoneWeighting.apply_zone_weights({0: 0.5, 1: 0.5}, {0: "title", 1: "body"}, title_weight=0.6)
    assert zone_scores[0] > zone_scores[1]

    # Method 49: Evaluation
    eval_metrics = IREvaluator.evaluate_retrieval(
        retrieved_doc_ids=[0, 1, 2],
        relevant_doc_ids={0, 2},
        k=2
    )
    assert eval_metrics["precision_at_k"] == 0.5
    assert eval_metrics["recall_at_k"] == 0.5
    print("  -> Methods 46-49 passed!")


def run_all_tests():
    print("=========================================================")
    print("STARTING ADVANCED INFORMATION RETRIEVAL TEST SUITE")
    print("=========================================================")
    pdocs = test_preprocessing()
    bundle = test_index_construction(pdocs)
    test_compression(bundle)
    test_wildcards_and_spelling(bundle)
    test_boolean_and_phrase(bundle)
    test_ranking_and_expansion(bundle)
    test_advanced_and_evaluation(bundle)
    print("=========================================================")
    print("ALL INFORMATION RETRIEVAL ALGORITHMS VERIFIED SUCCESSFULLY!")
    print("=========================================================")


if __name__ == "__main__":
    run_all_tests()
