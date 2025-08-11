## Northeastern University Chatbot — Enhanced GPU Edition

### Problem Statement

- Goal: Deliver accurate, up-to-date, and context-aware answers about Northeastern University with low latency and high reliability.
- Challenges:
  - University information is scattered across multiple sites and frequently changes.
  - Generic chatbots hallucinate and lack domain-specific recall and trustworthy citations.
  - Latency on CPU-bound pipelines is high; retrieval quality suffers without query reformulation.
- Use cases:
  - Prospective students: admissions, programs, tuition, scholarships.
  - Current students: policies, deadlines, co-op, course details.
  - Staff/visitors: offices, contacts, campus resources.

### Introduction

- Method overview:
  - GPU-accelerated RAG pipeline with hybrid retrieval (semantic + keyword), query expansion, reranking, and answer validation.
  - Confidence scoring and source attribution to improve trust.
  - Conversation history for contextual continuity; user feedback loop for continuous improvement.
- Datasets:
  - Scraped Northeastern University domains (main site and catalog) via Scrapy; stored as documents in ChromaDB with metadata (title, URL, timestamps).
- Model choices:
  - LLM: Local Ollama `llama2:7b` for cost control and on-GPU generation.
  - Embeddings: HuggingFace `all-MiniLM-L6-v2` (compact, fast; good quality/latency tradeoff) executed on GPU when available.
  - Considered alternatives: larger LLMs (higher VRAM cost), OpenAI APIs (recurring cost, data governance), larger embedding models (better recall but slower). Final choice optimizes cost and speed with sufficient quality.

### Methodology

- System architecture

```mermaid
graph TD
  A[Frontend (Port 3000)] --> B[FastAPI: Enhanced GPU API (Port 8001)]
  B --> C[ChromaDB (PersistentClient: ./chroma_data)]
  B --> D[Ollama (llama2:7b)]
  D --> E[NVIDIA GPU (CUDA)]
  B --> F[Query Expansion • Hybrid Search • Reranking • Confidence]
```

- Pipeline
  - Query Expansion: Generate up to 3 focused rewrites using the LLM to improve recall without drifting topic.
  - Hybrid Retrieval: For each rewrite, run semantic search (GPU embeddings) over ChromaDB and combine with keyword/BM25 signals; deduplicate and rerank by question-specific relevance.
  - Context Builder: Select top sections (~10 docs, ~12k chars) by term overlap and similarity.
  - Generation: Prompt LLM with strict instructions to answer only from context; validate and regenerate if response looks generic or off-topic.
  - Confidence: Weighted score combining similarity, document count, answer length, and source diversity.

- Confidence computation

\[ \text{confidence} = 0.4\,s + 0.2\,c + 0.2\,l + 0.2\,d \]

Where: \(s\) is average similarity, \(c\) is normalized doc count, \(l\) is normalized answer length, \(d\) is unique source diversity. Bounded to \([0,1]\).

- GPU optimization
  - Automatic CUDA detection with PyTorch; embeddings model runs on `cuda` when available, else CPU fallback.
  - Local LLM via Ollama reduces network latency and cost; 7B model fits consumer GPUs (6–12GB VRAM) with acceptable speed.
  - Caching of query/document embeddings to reduce redundant compute.

### Experiments and Results

- Setup
  - Hardware: NVIDIA RTX 3060 12GB (or comparable) with CUDA ≥11; 16GB system RAM.
  - Software: FastAPI + Uvicorn, Ollama `llama2:7b`, ChromaDB persistent mode, `all-MiniLM-L6-v2` embeddings.
  - Retrieval: Top-10 documents aggregated across expanded queries; context size ~12k chars.

- Metrics
  - Latency: end-to-end response time; search/context/LLM breakdown.
  - Retrieval quality: relevance of cited sources to the question (manual checks).
  - Confidence calibration: correlation between score and perceived answer quality.
  - User feedback: thumbs/rating and comment analysis.

- Performance (baseline vs enhanced GPU)

| Feature | Standard | Enhanced GPU |
|---------|----------|--------------|
| Response Time | 15–30s | 5–15s |
| GPU Acceleration | ❌ | ✅ |
| Query Expansion | ❌ | ✅ |
| Hybrid Search | Basic | Enhanced |
| Documents Analyzed | 5 | 10 |
| Confidence Scoring | Basic | Advanced |

- Key findings
  - GPU acceleration cuts typical latency to 5–15s while enabling deeper retrieval (10 docs).
  - Query expansion improves recall on narrowly phrased questions without topic drift when constrained by context.
  - Confidence scoring aligns with perceived quality and helps decide when to show or withhold answers.
  - Local LLM via Ollama materially reduces cost vs hosted APIs while meeting accuracy and speed targets.

### Conclusion and Future Work

- Contributions
  - A domain-specialized, GPU-accelerated RAG system for Northeastern University with hybrid retrieval, query expansion, calibrated confidence, and source grounding.
  - Persistent vector store (ChromaDB) + local LLM (Ollama) architecture that is cost-efficient and deployable on low-cost GPUs.
  - Frontend that surfaces system status, source citations, and confidence to build user trust.

- Limitations
  - Quality bounded by local LLM capability and scraped data freshness.
  - Long-form or multi-hop queries may exceed context limits; potential for partial answers.
  - GPU memory constraints limit model size and batch throughput on the cheapest hardware.

- Future work
  - Add cross-encoder reranking and lightweight rewriters to further improve precision.
  - Streaming responses and tool-use for structured queries (e.g., calendars, contacts).
  - Smarter chunking, section scoring, and citation mapping.
  - Multi-university, tenant-aware indexing and retrieval.
  - Low-cost deployment automation on RunPod/Vast with autoscaling, and static hosting for the frontend.

---

Contact: Abhishek Sagar Sanda · sanda.a@northeastern.edu