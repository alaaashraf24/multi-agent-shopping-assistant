from __future__ import annotations
import os
from typing import List
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel
from .core.models import SearchPlan, Product
from .core.ranker import rank_products
from .tools.tavily_tool import search_products
from .tools.scrapers import extract_product

def make_llm() -> LLM:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "anthropic":
        return LLM(model=os.getenv("ANTHROPIC_MODEL","claude-3-haiku-20240307"), api_key=os.getenv("ANTHROPIC_API_KEY"))
    if provider == "google":
        return LLM(model=os.getenv("GOOGLE_MODEL","gemini-2.0-flash-lite"), api_key=os.getenv("GOOGLE_API_KEY"))
    # default openai
    return LLM(model=os.getenv("OPENAI_MODEL","gpt-4o-mini"), api_key=os.getenv("OPENAI_API_KEY"))

def planner_agent(llm: LLM) -> Agent:
    return Agent(
        role="Shopping Planner",
        goal="Turn user input into a precise search plan with budget, brand, features, and rating thresholds.",
        backstory="Expert prompt engineer and retail analyst who crafts actionable search queries.",
        llm=llm,
        verbose=True,
    )

def search_agent(llm: LLM) -> Agent:
    return Agent(
        role="Marketplace Searcher",
        goal="Use Tavily to find the most relevant product URLs on Amazon.eg, Jumia, and Noon (Egypt).",
        backstory="Specialist in web search for Egyptian marketplaces.",
        llm=llm,
        verbose=True,
    )

def extractor_agent(llm: LLM) -> Agent:
    return Agent(
        role="Product Extractor",
        goal="Fetch pages and extract normalized product info (title, price EGP, rating, images).",
        backstory="Schema.org and DOM parsing expert.",
        llm=llm,
        verbose=True,
    )

def analyst_agent(llm: LLM) -> Agent:
    return Agent(
        role="Product Analyst",
        goal="Compare products based on constraints and quality to shortlist top candidates.",
        backstory="E-commerce analyst valuing quality and price fairness.",
        llm=llm,
        verbose=True,
    )

def reviewer_agent(llm: LLM) -> Agent:
    return Agent(
        role="Reviewer",
        goal="Summarize strengths/weaknesses, tradeoffs, and who each product is for.",
        backstory="Reads product pages and synthesizes key points for buyers.",
        llm=llm,
        verbose=True,
    )

def recommender_agent(llm: LLM) -> Agent:
    return Agent(
        role="Recommender",
        goal="Output a final recommendation JSON with top pick, 2 runner-ups, and reasoning.",
        backstory="Explains choices clearly and concisely.",
        llm=llm,
        verbose=True,
    )

# ---- Tasks ----
def make_tasks(planner: Agent, searcher: Agent, extractor: Agent, analyst: Agent, reviewer: Agent, recommender: Agent):
    plan_task = Task(
        description=(
            "Given the user_input, produce a JSON SearchPlan {query, brand?, max_price?, min_rating?, features[]}.
"
            "Prefer EGP and Egypt-specific terms. Keep query short and specific."
        ),
        expected_output="A compact JSON object for SearchPlan.",
        agent=planner,
        output_json=SearchPlan.model_json_schema(),  # hint
    )

    search_task = Task(
        description=(
            "Use Tavily to search for product pages on Amazon.eg, Jumia Egypt, and Noon Egypt based on the SearchPlan.query. "
            "Return a Python list of up to 12 URLs."
        ),
        expected_output="A list[str] of URLs.",
        agent=searcher,
    )

    extract_task = Task(
        description=(
            "For each URL, fetch page HTML and extract normalized fields: title, price (EGP), rating, review_count, images. "
            "Return a Python list of Product dicts."
        ),
        expected_output="A list[Product] serialized as dicts.",
        agent=extractor,
    )

    analyze_task = Task(
        description=(
            "Given extracted products and the SearchPlan constraints, rank and shortlist the best 5. "
            "Return the top 5 as a list of dicts."
        ),
        expected_output="Top-5 product dicts list.",
        agent=analyst,
    )

    review_task = Task(
        description=(
            "Summarize pros/cons and suitability for the shortlisted products in 5-8 concise bullet points total."
        ),
        expected_output="A brief markdown summary string.",
        agent=reviewer,
    )

    recommend_task = Task(
        description=(
            "Choose the single best product for the user. Output JSON: {best: Product, runners_up: [Product, Product], reasoning:str}."
        ),
        expected_output="Recommendation JSON string.",
        agent=recommender,
    )

    return plan_task, search_task, extract_task, analyze_task, review_task, recommend_task

# ---- Orchestration (glue code that actually executes tools) ----
def run_pipeline(user_input: str):
    llm = make_llm()
    planner = planner_agent(llm)
    searcher = search_agent(llm)
    extractor = extractor_agent(llm)
    analyst = analyst_agent(llm)
    reviewer = reviewer_agent(llm)
    recommender = recommender_agent(llm)

    plan_task, search_task, extract_task, analyze_task, review_task, recommend_task = make_tasks(planner, searcher, extractor, analyst, reviewer, recommender)

    crew = Crew(
        agents=[planner, searcher, extractor, analyst, reviewer, recommender],
        tasks=[plan_task, search_task, extract_task, analyze_task, review_task, recommend_task],
        process=Process.sequential,
        verbose=True,
    )

    # Step 1: plan
    plan_res = planner.llm.call(f"User input: {user_input}\nReturn JSON for SearchPlan with keys query, brand, max_price, min_rating, features.")
    # naive JSON extraction
    import json, re
    try:
        plan_json_str = re.search(r"{[\s\S]*}", plan_res).group(0)
        plan_data = json.loads(plan_json_str)
    except Exception:
        plan_data = {"query": user_input, "brand": None, "max_price": None, "min_rating": None, "features": []}
    plan = SearchPlan(**plan_data)

    # Step 2: search with Tavily
    urls = search_products(plan.query, max_results=12)

    # Step 3: extract
    products = []
    for u in urls:
        try:
            p = extract_product(u)
            if p:
                products.append(p)
        except Exception:
            continue

    # Step 4: rank
    from .core.ranker import rank_products
    ranked = rank_products(products, plan.brand, plan.max_price, plan.min_rating)[:5]

    # Step 5: review (LLM summarization over titles/price)
    ctx = "\n".join([f"- {p.title} | {p.price} EGP | {p.source}" for p in ranked])
    summary = reviewer.llm.call(f"Summarize pros/cons and who it's for across these products:\n{ctx}\nBe concise.")

    # Step 6: recommend
    best = ranked[0].model_dump() if ranked else None
    runners = [p.model_dump() for p in ranked[1:3]]
    reasoning = recommender.llm.call(
        f"Pick the best product for: brand={plan.brand}, max_price={plan.max_price}, min_rating={plan.min_rating}, features={plan.features}.\n"
        f"Candidates:\n{ctx}\nExplain decision in 3-5 sentences."
    )
    return {
        "plan": plan.model_dump(),
        "urls": urls,
        "products": [p.model_dump() for p in products],
        "top5": [p.model_dump() for p in ranked],
        "summary": summary,
        "recommendation": {"best": best, "runners_up": runners, "reasoning": reasoning}
    }
