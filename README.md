# Advanced Information Retrieval (IR) Search Engine

A full-stack, production-grade **Information Retrieval Search Engine** that allows users to upload any document (`.txt`, `.pdf`, `.docx`, `.csv`), enter search queries, and search with genuine IR algorithms while viewing live, microsecond execution logs in a **VS Code-styled terminal interface**.

---

## 1. System Overview

- **Real-Time Execution Terminal**: Streams live events from the backend via WebSockets / Server-Sent Events (SSE). Every method displays status (`COMPLETED`, `RUNNING`, `SKIPPED`, `FAILED`), timestamps, execution duration, and clickable algorithm inspectors.
- **Strict Method Execution Fidelity**: Indexing-time methods run once during file upload; query-time methods activate dynamically based on the query syntax (single-word, phrase, boolean, wildcard, proximity, ranked). Skipped methods explain *why* they were skipped for that specific query.
- **Full Support for 45+ Information Retrieval Methods**: Every single method from IR theory is genuinely implemented without mock or dummy code.

---

## 2. Technology Stack

### Frontend
- **Framework**: React.js 19 with TypeScript
- **Bundler & Dev Server**: Vite 8
- **Styling**: Tailwind CSS v4 (Dark Navy / Charcoal developer theme: `#090d16`, `#0f1422`, `#1e293b`, Cyan accents)
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Streaming**: Native WebSocket Client with automatic Server-Sent Events (SSE) fallback

### Backend
- **Framework**: Python 3.13, FastAPI, Uvicorn
- **NLP & Parsing**: Porter Stemmer, pypdf (PDF parsing), python-docx (DOCX parsing), csv/pandas (CSV parsing)
- **Scientific Computing**: NumPy, Scikit-Learn (TruncatedSVD for Latent Semantic Indexing), SciPy
- **Protocols**: Async WebSockets (`/ws/execution`), Server-Sent Events (`/api/stream/events`), REST API

---

## 3. The 45 Information Retrieval Methods Implemented

### A. Text Processing and Normalization
1. **Document Parsing**: Multi-format text extraction (TXT, PDF, DOCX, CSV) and segmentation into discrete passages, tracking line and page numbers.
2. **Tokenization**: Word segmentation with punctuation isolation, tracking character spans and token positions.
3. **Case Folding**: Standardizes characters to unified lowercase for case-insensitive matching.
4. **Stop Word Removal**: Filters out 179 high-frequency, low-entropy functional words.
5. **Stemming**: Complete, authentic implementation of the Porter Stemming Algorithm (1980).
6. **Document ID Assignment**: Assigns sequential integer identifiers (`doc_0`, `doc_1`, ...) to each segmented passage.

### B. Index Construction
7. **Term-Document Pair Generation**: Emits flat `(term, doc_id)` tuples from tokenized segments.
8. **Sorting**: Lexicographically sorts pairs by term as primary key and doc_id as secondary key.
9. **Merging Duplicate Terms**: Groups identical pairs into single postings and computes term frequencies.
10. **Term Frequency Calculation**: Computes $tf(t, d)$ across all terms and documents.
11. **Dictionary Construction**: Vocabulary lexicon mapping each unique term to document frequency ($df_t$) and postings list pointer.
12. **Inverted Index Construction**: Core mapping of dictionary terms to ordered postings lists.
13. **Postings List Construction**: Linked and array-backed postings nodes containing `doc_id` and $tf$.
14. **Biword Index**: Indexes consecutive token pairs $(w_i, w_{i+1}) \to doc\_ids$ for accelerated 2-word phrase lookup.
15. **Positional Index**: Stores exact token offset positions: $term \to \{doc\_id: [pos_0, pos_1, \dots]\}$ for exact phrase matching and arbitrary proximity verification.
16. **Skip Pointers**: Augments postings lists with skip pointers at $\lfloor\sqrt{L}\rfloor$ intervals for fast sub-linear intersection.

### C. Index Optimization and Compression
17. **Gap Encoding**: Computes difference d-gaps ($d_1, d_2 - d_1, d_3 - d_2, \dots$) to minimize integer magnitudes.
18. **Variable Byte (VB) Encoding**: Byte-aligned compression using 7 payload bits and 1 continuation bit (achieving 75%+ space savings).
19. **Elias Gamma Encoding**: Bit-level compression representing numbers as unary length followed by binary offset.
20. **Dictionary-as-String**: Concatenates lexicon terms into a single string buffer with offset pointers.
21. **Blocking**: Groups dictionary terms into blocks of size $k=4$, storing string offsets only for block heads.
22. **Front Coding**: Prefix compression on adjacent sorted terms sharing common roots.
23. **Dynamic Indexing**: In-memory auxiliary index with periodic logarithmic merge into main index.

### D. Query Processing and Search
24. **Query Parsing**: Analyzes query syntax into AST detecting Boolean clauses (`AND`, `OR`, `NOT`), quoted phrases (`"..."`), proximity (`NEAR/k`), and wildcards (`*`).
25. **Query Tokenization**: Tokenizes query and applies identical normalization (case folding, stop words, stemming).
26. **Wildcard Query Processing**: Evaluates prefix, suffix, and infix wildcard patterns.
27. **Permuterm Index**: Rotated circular shift index terminated with `$` for $O(1)$ wildcard candidate lookup.
28. **Bigram / N-gram Processing**: Splits wildcard queries into character bigrams, retrieves candidates, and applies regex post-filtering.
29. **Spelling Correction**: Suggests closest vocabulary words for misspelled or out-of-vocabulary query terms.
30. **Edit Distance**: Levenshtein distance dynamic programming matrix + Weighted Edit Distance (keyboard adjacency penalty).
31. **N-gram Overlap**: Character trigram overlap similarity between terms.
32. **Jaccard Similarity**: Set coefficient $\frac{|A \cap B|}{|A \cup B|}$ on character n-grams + Soundex phonetic matching.
33. **Phrase Query Processing**: Verifies exact consecutive token offsets ($pos_{i+1} = pos_i + 1$) using the Positional Index.
34. **Proximity Search**: Verifies whether two terms appear within window distance $k$ ($|pos_1 - pos_2| \le k$).
35. **Boolean Retrieval**: Set-theoretic logic evaluation supporting conjunctive `AND`, disjunctive `OR`, and difference `NOT`.
36. **Postings List Intersection**: Fast two-pointer intersection leaping forward using skip pointers.
37. **Query Optimization**: Orders conjunctive Boolean terms in ascending order of document frequency ($df$) to minimize intermediate sets.

### E. Ranked Retrieval
38. **Term Frequency (TF)**: Sublinear weighting $1 + \log_{10}(tf)$ when $tf > 0$.
39. **Inverse Document Frequency (IDF)**: Collection rarity $\log_{10}(N / df_t)$.
40. **TF-IDF**: Composite weighting $w_{t,d} = (1 + \log_{10}(tf_{t,d})) \times \log_{10}(N / df_t)$.
41. **Vector Space Model**: High-dimensional vector space with Euclidean ($L_2$) length normalization.
42. **Cosine Similarity**: Angular dot product $\cos(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\| \|\vec{d}\|}$ using Accumulator tables.
43. **Document Ranking**: Sorts candidate passages in descending order of relevance score.
44. **Top-K Retrieval**: Min-heap priority queue selection of the top $K$ scoring passages without full collection sorting.

### F. Search Improvement and Evaluation
45. **Query Expansion & Relevance Feedback**: Rocchio algorithm $\vec{q}_m = \alpha \vec{q}_0 + \beta \frac{1}{|D_r|}\sum \vec{d} - \gamma \frac{1}{|D_{nr}|}\sum \vec{d}$ and Pseudo-Relevance Feedback (PRF).
46. **Latent Semantic Indexing (LSI)**: Truncated SVD dimensionality reduction uncovering latent semantic concepts.
47. **Cluster Pruning**: $\sqrt{N}$ leader-follower clustering for fast approximate Top-K search.
48. **Zone Weighting**: Linear combination weighting matches in title/header zones higher than regular body text.
49. **Evaluation Metrics**: Formal IR benchmark calculating Precision@K, Recall@K, F-measure ($F_1$), Mean Average Precision (MAP), and R-Precision.

---

## 4. Installation and Setup

### Prerequisites
- **Python**: 3.10+ (tested on Python 3.13)
- **Node.js**: v18+ (tested on v22)
- **npm**: 9+

### Backend Installation

1. Open a terminal and navigate to the project root:
   ```bash
   cd c:/Users/DELL/Desktop/search
   ```

2. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the backend unit and integration test suite:
   ```bash
   python backend/test_ir.py
   python backend/test_e2e.py
   ```

4. Start the FastAPI backend server:
   ```bash
   python backend/main.py
   ```
   The backend will start at `http://127.0.0.1:8000`. Swagger API docs are available at `http://127.0.0.1:8000/docs`.

---

### Frontend Installation

1. In a separate terminal, navigate to the `frontend/` directory:
   ```bash
   cd c:/Users/DELL/Desktop/search/frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
   Open your browser at `http://localhost:5173`.

---

## 5. Working Example Walkthrough

1. **Load or Upload a Document**:
   - Drag and drop your own `.txt`, `.pdf`, `.docx`, or `.csv` file into the upload zone.
   - Or click **One-Click Samples** to load `information_retrieval_handbook.txt` or `computer_science_encyclopedia.docx`.
   - Watch the **Live Execution Terminal** stream indexing events in real time:
     `Document Parsing` $\to$ `Tokenization` $\to$ `Case Folding` $\to$ `Stop Words` $\to$ `Stemming` $\to$ `Inverted Index` $\to$ `Variable Byte Compression`.
2. **Execute a Ranked Search**:
   - Enter `information retrieval` and click **Search**.
   - See matching passages with highlighted keywords, exact line/page references, Cosine similarity percentage, and TF-IDF weights.
   - Click **View TF/IDF Breakdown** on any result to inspect the exact formula contributions.
3. **Execute an Exact Phrase Search**:
   - Enter `"information retrieval"` with quotes.
   - The terminal logs `Method 33: Phrase Query Processing` verifying consecutive token offsets in the Positional Index.
4. **Execute a Boolean Search**:
   - Enter `inverted AND index NOT compression`.
   - The terminal logs `Method 35: Boolean Retrieval`, `Method 36: Postings Intersection`, and `Method 37: Query Optimization`.
5. **Execute a Wildcard Search**:
   - Enter `retriev*`.
   - The terminal logs `Method 26: Wildcard Processing`, `Method 27: Permuterm Index`, and `Method 28: Bigram Post-Filtering`.
6. **Execute a Typo Search**:
   - Enter `retreival`.
   - Notice the spell checker banner: *"Did you mean: 'retrieval'?"* using Levenshtein edit distance and Soundex.
7. **Inspect any Method**:
   - Click on any log event in the terminal or card in the **IR Pipeline** tab to open the full mathematical explanation, formulas, and trace payloads.
8. **Run Benchmark**:
   - Click the **Benchmark** button in the top navigation to evaluate Precision, Recall, F1, MAP, and R-Precision across test queries.
#   A d v a n c e d - I n f o r m a t i o n - R e t r i e v a l - E n g i n e  
 