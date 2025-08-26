# ShopSmart-EG 🛍️ — Multi‑Agent Shopping Assistant (Amazon.eg, Jumia, Noon Egypt)

A resume‑ready, Streamlit‑deployed **multi‑agent** shopping assistant that:
- Searches **Amazon.eg**, **Jumia (Egypt)**, and **Noon (Egypt)** in real time using **Tavily**.
- Extracts product details from product pages (price, rating, title, availability, images).
- Ranks/compares and returns a concise recommendation with reasoning.
- Ships with a polished Streamlit GUI and a modular, interview‑friendly codebase.

> Built to showcase Generative AI + LLM engineering skills: multi‑agent orchestration (CrewAI), tool design, web extraction, ranking, and Streamlit UX.

---

## ✨ Highlights
- **Agents** (CrewAI): *Planner*, *Searcher*, *Extractor*, *Analyst*, *Reviewer*, *Recommender*.
- **Real‑time search** via **Tavily** (no Serper; works in Egypt).
- **Target sites**: `amazon.eg`, `jumia.com.eg`, `noon.com/egypt-en`.
- **Schema‑aware extraction** (JSON‑LD via `extruct`) + fallback parsing with BeautifulSoup.
- **Ranking** by price/quality + constraint satisfaction (budget, brand, features).
- **Streamlit UI** with compare table, per‑item drill‑down, and final recommendation.
- **Resume‑ready** structure, typing, tests, and clear README.

---

## 🧱 Architecture

```mermaid
flowchart LR
    U[User] -->|Query & Filters| P(Planner Agent)
    P -->|search queries| S(Search Agent via Tavily)
    S -->|urls (amazon.eg, jumia, noon)| X(Extractor Agent)
    X -->|normalized products| A(Analyst/Ranker Agent)
    A -->|top candidates| R(Reviewer/Summarizer Agent)
    R -->|final summary| C(Recommender Agent)
    C -->|result JSON| UI(Streamlit UI)
```

**Agents implemented with CrewAI** and custom tools for Tavily search and per‑site extraction.

---

## 🚀 Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# fill in TAVILY_API_KEY and an LLM key (OpenAI/Anthropic/Google)
streamlit run app/streamlit_app.py
```

> If you don’t have OpenAI/Anthropic/Google keys, set `LLM_PROVIDER=google` and use a free Gemini tier if available in your region, or switch to a local model via LiteLLM (optional, see code comments).

---

## ⚙️ Configuration

- `.env` controls keys and provider:
  - `TAVILY_API_KEY` (required for search)
  - `LLM_PROVIDER` one of: `openai`, `anthropic`, `google`
  - Models: `OPENAI_MODEL`, `ANTHROPIC_MODEL`, `GOOGLE_MODEL`

- **Domains searched** (hard‑restricted): `amazon.eg`, `jumia.com.eg`, `noon.com/egypt-en`

---

## 🧩 Repo Structure

```
shopsmart-eg/
├─ app/
│  └─ streamlit_app.py
├─ shopsmart/
│  ├─ __init__.py
│  ├─ pipeline.py
│  ├─ agents.py
│  ├─ core/
│  │  ├─ models.py
│  │  ├─ ranker.py
│  │  └─ utils.py
│  └─ tools/
│     ├─ tavily_tool.py
│     └─ scrapers.py
├─ tests/
│  └─ test_extractors.py
├─ .env.example
├─ requirements.txt
├─ LICENSE
└─ README.md
```

---

## 🔐 Legal & Ethics

- Respect targets’ **robots.txt** and **Terms of Service**. This project requests only a few pages, adds backoff, and prefers public metadata (JSON‑LD). Scraping any site may be disallowed; you are responsible for compliance.
- For Amazon, consider the **Product Advertising API** for full‑fidelity data (requires Associate account). This demo uses public pages.

---

## 🧪 Tests

```bash
pytest -q
```

---

## 📄 Resume Tips

- Emphasize: *multi‑agent orchestration (CrewAI)*, *tooling (Tavily + Extractors)*, *schema parsing*, *ranking*, and *Streamlit UX*.
- Include a GIF/screenshot of the Streamlit app.
- Add a section on **limitations** (anti‑bot measures, rate limits) and **future work** (RAG over historical prices, LangGraph orchestration, async scraping, vector search).

---
