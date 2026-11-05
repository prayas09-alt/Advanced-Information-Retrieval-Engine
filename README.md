# 🔍 Advanced Information Retrieval Search Engine

A full-stack, production-grade **Information Retrieval (IR) Search Engine** built with React + FastAPI. Upload any document, run intelligent searches using 45+ genuine IR algorithms, and watch every method execute in real time through a **VS Code-style live terminal**.

---

## ✨ Features

- 📄 **Multi-format Document Upload** — TXT, PDF, DOCX, CSV with drag-and-drop
- 🧠 **45+ IR Algorithms** — Every method genuinely implemented, never mocked
- 🖥️ **Live Execution Terminal** — Real-time WebSocket log stream with timestamps
- 🔎 **Rich Query Support** — Single word, phrase, boolean, wildcard, proximity
- 📊 **Search Analytics** — TF-IDF scores, cosine similarity, ranking breakdown
- 🔧 **IR Pipeline Dashboard** — Visual pipeline with per-method status and explanations
- 🧪 **Evaluation Metrics** — Precision, Recall, F1, MAP, R-Precision

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion, Lucide Icons |
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **NLP / IR** | NLTK (Porter Stemmer), pypdf, python-docx, NumPy, scikit-learn |
| **Streaming** | WebSockets (`/ws/execution`) + SSE fallback (`/api/stream/events`) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ (tested on 3.13)
- Node.js v18+ (tested on v22)
- npm 9+

---

### 1. Clone the Repository

```bash
git clone https://github.com/prayas09-alt/Advanced-Information-Retrieval-Engine.git
cd Advanced-Information-Retrieval-Engine
```

---

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# (Optional) Run tests to verify all 45 IR methods
python backend/test_ir.py
python backend/test_e2e.py

# Start the backend server
python backend/main.py
```

Backend runs at → `http://127.0.0.1:8000`  
Swagger API docs → `http://127.0.0.1:8000/docs`

---

### 3. Frontend Setup

```bash
# In a separate terminal
cd frontend

npm install
npm run dev
```

Frontend runs at → `http://localhost:5173`

---

### ⚡ One-Command Start (Windows)

```bash
run_all.bat
```

This opens two terminals — one for the backend, one for the frontend.

---

## 📂 Project Structure

```
search/
├── backend/
│   ├── main.py                  # FastAPI app, WebSocket, REST routes
│   ├── execution_logger.py      # Live event broadcaster (49-method catalog)
│   ├── text_extractor.py        # TXT / PDF / DOCX / CSV parser
│   ├── preprocessing.py         # Methods 1–6 (tokenize, stem, stop words)
│   ├── indexer.py               # Methods 7–16 (inverted/positional index)
│   ├── compression.py           # Methods 17–23 (VB, Elias Gamma, front coding)
│   ├── query_processor.py       # Methods 24–25, 33–34
│   ├── wildcard_search.py       # Methods 26–28 (permuterm, bigram)
│   ├── spelling_correction.py   # Methods 29–32 (Levenshtein, Soundex, Jaccard)
│   ├── boolean_retrieval.py     # Methods 35–37
│   ├── tfidf.py                 # Methods 38–40
│   ├── vector_space.py          # Method 41
│   ├── cosine_similarity.py     # Method 42
│   ├── ranking.py               # Methods 43–44
│   ├── query_expansion.py       # Method 45 (Rocchio PRF)
│   ├── advanced_ir.py           # Methods 46–48 (LSI, Cluster Pruning, Zone Weighting)
│   ├── evaluation.py            # Method 49 (Precision, Recall, MAP, F1)
│   ├── requirements.txt
│   ├── test_ir.py
│   └── test_e2e.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── SearchResults.tsx
│   │   │   ├── LiveTerminal.tsx
│   │   │   ├── MethodDashboard.tsx
│   │   │   ├── PipelineVisualizer.tsx
│   │   │   ├── SearchAnalytics.tsx
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   └── types/ir.ts
│   ├── package.json
│   └── vite.config.ts
│
├── run_all.bat
├── run_backend.bat
├── run_frontend.bat
└── README.md
```

---

## 🧠 45 IR Methods Implemented

### A — Text Processing & Normalization
| # | Method | Description |
|---|---|---|
| 1 | Document Parsing | Multi-format extraction with line/page tracking |
| 2 | Tokenization | Word segmentation with character span tracking |
| 3 | Case Folding | Lowercase normalization |
| 4 | Stop Word Removal | Filters 179 high-frequency words |
| 5 | Stemming | Full Porter Stemming Algorithm (1980) |
| 6 | Document ID Assignment | Sequential passage identifiers |

### B — Index Construction
| # | Method | Description |
|---|---|---|
| 7 | Term-Document Pair Generation | Flat `(term, doc_id)` tuples |
| 8 | Sorting | Lexicographic ordering by term then doc_id |
| 9 | Merging Duplicate Terms | Groups pairs and computes frequencies |
| 10 | Term Frequency Calculation | `tf(t, d)` across all documents |
| 11 | Dictionary Construction | Vocabulary → `df` and postings pointer |
| 12 | Inverted Index Construction | Core term → postings mapping |
| 13 | Postings List Construction | Linked nodes with `doc_id` and `tf` |
| 14 | Biword Index | Consecutive token pair `(w_i, w_i+1)` → doc_ids |
| 15 | Positional Index | `term → {doc_id: [pos_0, pos_1, ...]}` |
| 16 | Skip Pointers | √L interval skip augmentation |

### C — Compression
| # | Method | Description |
|---|---|---|
| 17 | Gap Encoding | d-gaps to minimize integer magnitudes |
| 18 | Variable Byte Encoding | 7-bit payload + 1 continuation bit (75%+ savings) |
| 19 | Elias Gamma Encoding | Bit-level unary + binary compression |
| 20 | Dictionary-as-String | Single buffer with offset pointers |
| 21 | Blocking | Block heads with k=4 grouping |
| 22 | Front Coding | Prefix compression on sorted terms |
| 23 | Dynamic Indexing | Auxiliary index with log-merge |

### D — Query Processing
| # | Method | Description |
|---|---|---|
| 24 | Query Parsing | AST for boolean, phrase, proximity, wildcard |
| 25 | Query Tokenization | Normalized query terms |
| 26 | Wildcard Query Processing | `retriev*` expansion |
| 27 | Permuterm Index | Rotation-based wildcard lookup |
| 28 | Bigram / N-gram Processing | Bigram post-filtering |
| 29 | Spelling Correction | Levenshtein + Soundex |
| 30 | Edit Distance | Weighted Levenshtein distance |
| 31 | N-gram Overlap | Bigram set comparison |
| 32 | Jaccard Similarity | Overlap coefficient for suggestions |
| 33 | Phrase Query Processing | Consecutive position verification |
| 34 | Proximity Search | NEAR/k operator using positional index |
| 35 | Boolean Retrieval | AND, OR, NOT evaluation |
| 36 | Postings List Intersection | Two-pointer with skip pointers |
| 37 | Query Optimization | Ascending `df` ordering |

### E — Ranked Retrieval
| # | Method | Description |
|---|---|---|
| 38 | Term Frequency (TF) | `1 + log10(tf)` sublinear weighting |
| 39 | Inverse Document Frequency (IDF) | `log10(N / df_t)` |
| 40 | TF-IDF | Composite term weight |
| 41 | Vector Space Model | L2-normalized document vectors |
| 42 | Cosine Similarity | Angular dot product with accumulator tables |
| 43 | Document Ranking | Descending relevance sort |
| 44 | Top-K Retrieval | Min-heap priority queue selection |

### F — Evaluation & Improvement
| # | Method | Description |
|---|---|---|
| 45 | Query Expansion (Rocchio PRF) | α·q + β·relevant − γ·non-relevant |
| 46 | Latent Semantic Indexing (LSI) | Truncated SVD dimensionality reduction |
| 47 | Cluster Pruning | √N leader-follower approximate search |
| 48 | Zone Weighting | Title/header zones weighted higher |
| 49 | Evaluation Metrics | Precision, Recall, F1, MAP, R-Precision |

---

## 🔎 Supported Query Types

| Query | Example | Methods Activated |
|---|---|---|
| Single word | `retrieval` | Inverted Index, TF-IDF, Cosine |
| Multi-word | `information retrieval` | Ranked Retrieval, VSM |
| Exact phrase | `"information retrieval"` | Positional Index, Phrase Processing |
| Boolean | `inverted AND index NOT compression` | Boolean Retrieval, Postings Intersection |
| Wildcard | `retriev*` | Permuterm Index, Bigram Filter |
| Proximity | `information NEAR/3 retrieval` | Positional Index, Proximity Search |
| Misspelled | `retreival` | Spelling Correction, Edit Distance |

---

## 🖥️ Live Terminal Output Example

```
[08:45:01] SYSTEM    Search engine initialized
[08:45:02] FILE      document.pdf uploaded successfully (42 KB)
[08:45:02] PARSER    Extracting text from PDF — 318 passages extracted
[08:45:03] TOKENIZER Tokenizing 4,821 tokens
[08:45:03] NORMALIZE Applying case folding
[08:45:03] STOPWORDS Removing 179 stop words — 2,944 tokens remain
[08:45:03] STEMMER   Porter Stemming applied — 1,203 unique stems
[08:45:04] INDEXER   Building inverted index — 1,203 terms
[08:45:04] INDEXER   Building positional index
[08:45:04] COMPRESS  Variable Byte Encoding — 75.2% space saved
[08:45:05] QUERY     Received: "information retrieval"
[08:45:05] PARSER    Detected: ranked multi-word query
[08:45:05] SEARCH    Postings retrieved for 2 terms
[08:45:06] RANKING   TF-IDF + Cosine Similarity computed
[08:45:06] RANKING   Top-10 passages selected via min-heap
[08:45:06] COMPLETE  Search completed in 0.043s — 10 results
```

---

## 📊 Search Result Card

Each result displays:

- Matched passage with highlighted keywords
- Line number (TXT) or page number (PDF)
- **TF**, **IDF**, **TF-IDF** scores
- **Cosine similarity** percentage
- Ranking position

---

## 🧪 Running Tests

```bash
# Unit tests — verifies all 49 IR methods
python backend/test_ir.py

# End-to-end API tests
python backend/test_e2e.py
```

Expected output: all tests pass, `EXIT 0`.

---

## 📸 UI Overview

| Panel | Description |
|---|---|
| **Top Nav** | App logo, file status, system status |
| **Left Sidebar** | Search history, uploaded files, IR method list |
| **Main Content** | Search bar, results, analytics dashboard |
| **Right Panel** | Live execution terminal + pipeline progress |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 👤 Author

**Prayas** — [@prayas09-alt](https://github.com/prayas09-alt)

> Built as a comprehensive demonstration of Information Retrieval theory applied in a real-world full-stack application.
