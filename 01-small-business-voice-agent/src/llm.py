import asyncio
import json
import re
from pathlib import Path
from time import perf_counter

from fastmcp import Client
from groq import Groq

from src.config import get_groq_config
from src.mcp_server import mcp


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "products.json"

STOPWORDS = {
    "the", "and", "for", "under", "below", "less", "than",
    "show", "me", "with", "a", "an", "in", "of", "to",
    "do", "you", "have", "find", "products", "product",
}

STOCK_PATTERN = re.compile(
    r"\b(stock|available|availability|in stock|out of stock)\b",
    re.IGNORECASE,
)


def load_products() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def retrieve_products(question: str) -> list[dict]:
    products = load_products()
    question_lower = question.lower()

    budget_match = re.search(
        r"(?:under|below|less than)\s*[₹]?\s*([\d,]+)",
        question_lower,
    )
    budget = (
        int(budget_match.group(1).replace(",", ""))
        if budget_match
        else None
    )

    search_text = re.sub(
        r"(?:under|below|less than)\s*[₹]?\s*[\d,]+",
        "",
        question_lower,
    )
    keywords = [
        word for word in re.findall(r"[a-z]+", search_text)
        if len(word) > 2 and word not in STOPWORDS
    ]

    matches = []
    for product in products:
        searchable_text = (
            f"{product['name']} {product['category']} "
            f"{product['description']}"
        ).lower()

        if (
            all(word in searchable_text for word in keywords)
            and (budget is None or product["price_inr"] < budget)
        ):
            matches.append(product)

    return matches


def resolve_product_id(question: str) -> str | None:
    products = load_products()
    question_lower = question.lower()

    # Prefer an explicit product ID.
    id_match = re.search(r"\bP\d+\b", question, re.IGNORECASE)
    if id_match:
        product_id = id_match.group().upper()
        if any(p["id"] == product_id for p in products):
            return product_id
        return None

    # Otherwise select a uniquely best match against product names.
    question_words = set(re.findall(r"[a-z0-9]+", question_lower))
    scores = []

    for product in products:
        name_words = set(re.findall(r"[a-z0-9]+", product["name"].lower()))
        score = len(question_words & name_words)
        if score:
            scores.append((score, product["id"]))

    if not scores:
        return None

    best_score = max(score for score, _ in scores)
    best_ids = [
        product_id for score, product_id in scores
        if score == best_score
    ]

    return best_ids[0] if len(best_ids) == 1 else None


async def call_stock_tool(product_id: str) -> dict:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_product_stock",
            {"product_id": product_id},
        )

        if result.is_error or not isinstance(result.data, dict):
            raise RuntimeError("MCP stock-check tool failed.")

        return result.data


def generate_answer(question: str) -> dict:
    api_key, model = get_groq_config()
    client = Groq(api_key=api_key)

    mcp_ms = 0.0
    used_mcp_tool = False

    if STOCK_PATTERN.search(question):
        product_id = resolve_product_id(question)

        if product_id is None:
            return {
                "answer": (
                    "Which product do you mean? Please provide its name "
                    "or a product ID such as P001, P002, or P003."
                ),
                "retrieval_ms": 0.0,
                "latency_ms": 0.0,
                "mcp_latency_ms": 0.0,
                "model": model,
                "retrieved_count": 0,
                "products": [],
                "used_mcp_tool": False,
            }

        mcp_start = perf_counter()
        stock_result = asyncio.run(call_stock_tool(product_id))
        mcp_ms = (perf_counter() - mcp_start) * 1000
        used_mcp_tool = True

        context = {"stock_check": stock_result}
        products = [stock_result] if stock_result.get("found") else []
        retrieval_ms = 0.0

        grounding_rule = (
            "Use the stock_check result as the source of truth for "
            "availability and price. Do not invent stock information."
        )
    else:
        retrieval_start = perf_counter()
        products = retrieve_products(question)
        retrieval_ms = (perf_counter() - retrieval_start) * 1000

        context = {"products": products}
        grounding_rule = (
            "Answer using only the supplied product records. "
            "If there are no matches, say so. Never invent prices or stock."
        )

    prompt = (
        "You are a small-business product assistant. "
        f"{grounding_rule}\n\n"
        f"Retrieved data:\n{json.dumps(context, ensure_ascii=False)}\n\n"
        f"Customer question: {question}"
    )

    llm_start = perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Give concise, accurate, evidence-grounded answers.",
            },
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=256,
    )
    llm_ms = (perf_counter() - llm_start) * 1000

    return {
        "answer": (response.choices[0].message.content or "").strip(),
        "retrieval_ms": round(retrieval_ms, 2),
        "latency_ms": round(llm_ms, 2),
        "mcp_latency_ms": round(mcp_ms, 2),
        "model": model,
        "retrieved_count": len(products),
        "products": products,
        "used_mcp_tool": used_mcp_tool,
    }
