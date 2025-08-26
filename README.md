# 🛒 Multi-Agent Shopping Assistant (GenAI + Streamlit)

A **multi-agent Generative AI shopping assistant** that helps users find the best deals on **Amazon Egypt, Jumia, and Noon** using **real-time search** powered by [Tavily](https://tavily.com/) and **reasoning with Gemini LLM**.  
Built with **Streamlit** for an interactive GUI and **optional voice input** for a hands-free experience.

---

## ✨ Features
- 🤖 **Multi-Agent Orchestration** – specialized AI agents for product search, filtering, and recommendation.  
- 🔎 **Real-Time Web Search** – live product data from **Amazon Egypt, Jumia, Noon** via Tavily API.  
- 🧠 **LLM Reasoning** – Google **Gemini** evaluates, compares, and summarizes options.  
- 🎨 **Streamlit GUI** – clean, interactive interface with filters (budget, rating, brand, features).  
- 🎤 **Voice Input (Optional)** – powered by `streamlit-webrtc` + `SpeechRecognition`.  
- 🔐 **Secure API Handling** – credentials stored in `.streamlit/secrets.toml`.  

---

## 🏗 Architecture

```mermaid
flowchart TD
    User[User: text/voice query] --> UI[Streamlit App]
    UI --> Agents[Multi-Agent System]
    Agents -->|Query| Tavily[Tavily Search API]
    Tavily --> Agents
    Agents -->|Reasoning| Gemini[Google Gemini LLM]
    Gemini --> Agents
    Agents --> UI
    UI --> User[Results + Recommendations]
````

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/alaaashraf24/multi-agent-shopping-assistant.git
cd multi-agent-shopping-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

Create `.streamlit/secrets.toml`:

```toml
TAVILY_API_KEY = "your_tavily_key_here"
GOOGLE_API_KEY = "your_gemini_key_here"
GOOGLE_MODEL = "gemini-2.0-flash-lite"
LLM_PROVIDER = "google"
```

### 4. Run the app

```bash
streamlit run app/streamlit_app.py
```

---

## 🧑‍💻 Skills Demonstrated

This project highlights key skills for **Generative AI & LLM Engineer roles**:

* **Multi-Agent Systems**: Orchestrating specialized AI agents for task division.
* **Generative AI (Gemini)**: Using LLMs for reasoning and summarization.
* **Real-Time Web Integration**: Live product data via Tavily API.
* **MLOps for Apps**: Secrets management (`.streamlit/secrets.toml`), clean repo structure.
* **Interactive UIs**: Streamlit dashboards with filters, visualization, and voice input.
* **Deployment-Ready**: Packaged for GitHub + Streamlit Cloud.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

