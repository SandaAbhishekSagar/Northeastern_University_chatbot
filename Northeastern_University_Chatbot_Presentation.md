# Northeastern University Chatbot: An AI-Powered Information Assistant

---

## Slide 1: Project Title & Team Member

**Northeastern University Chatbot: An AI-Powered Information Assistant**  
**Team Member:**  
Abhishek Sagar Sanda  
sanda.a@northeastern.edu

---

## Slide 2: Motivation & Problem Statement

- **NLP Problem:**  
  How can we provide accurate, up-to-date, and context-aware answers about Northeastern University using AI?
- **Why is it important?**  
  - University info is scattered and hard to search.
  - Students, staff, and visitors need reliable, fast answers.
  - Existing chatbots lack domain focus, confidence scoring, and feedback loops.

---

## Slide 3: Background / Related Work

- **RAG: Retrieval-Augmented Generation** (Lewis et al., 2020)
- **ChromaDB:** Open-source vector database for semantic search
- **IBM Watson Assistant for Education:** General-purpose university chatbots
- **Gap:**  
  Most systems lack domain-specific query expansion, confidence scoring, and user feedback analytics tailored for university settings.

---

## Slide 4: Dataset(s)

- **Primary Data:**  
  - Scraped content from Northeastern University websites (main site, course catalog, etc.)
  - Size: Thousands of documents, hundreds of thousands of words
  - Data: Web pages, FAQs, policy docs, program descriptions
- **Collection:**  
  - Automated web scraping (Scrapy)
  - Ongoing updates to keep data fresh
- **Annotation:**  
  - User feedback (ratings, comments) collected during chatbot use

---

## Slide 5: Proposed Approach

- **Architecture:**  
  - Hybrid RAG: Combines semantic (embedding-based) and keyword search
  - Query expansion using LLM (Ollama, llama2:7b)
  - Confidence scoring (multi-factor: similarity, coverage, answer quality)
  - User feedback loop for continuous improvement
- **Models/Methods:**  
  - Transformer-based embeddings (MiniLM)
  - Local LLM for answer generation
  - ChromaDB for fast vector search

---

## Slide 6: Evaluation Plan

- **Metrics:**  
  - Answer accuracy (manual review, user feedback)
  - Confidence score correlation with user ratings
  - Coverage: % of questions answered with high confidence
  - User satisfaction: Average feedback rating
- **Qualitative:**  
  - Review of low-confidence or low-rated answers
  - Analysis of common user issues

---

## Slide 7: Timeline & Milestones

- **Week 1:** Data scraping, cleaning, and ingestion
- **Week 2:** Model integration (embeddings, LLM), basic search
- **Week 3:** Implement confidence scoring, feedback collection
- **Week 4:** Frontend integration, user testing, analytics
- **Week 5:** Final evaluation, documentation, and presentation

---

## Slide 8: Challenges & Open Questions

- **Risks:**  
  - Keeping scraped data up-to-date
  - Handling ambiguous or out-of-domain questions
  - Balancing precision and recall in hybrid search
- **Feedback Needed:**  
  - Are our evaluation metrics sufficient?
  - Suggestions for improving user feedback collection or analytics?

---

## Slide 9: System Diagram / Demo Screenshot

- **Figure:**  
  - [Insert system architecture diagram: Frontend ↔ API ↔ ChromaDB ↔ LLM]
  - Or a screenshot of the chatbot in action

--- 