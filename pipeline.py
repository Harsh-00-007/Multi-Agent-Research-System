from langchain_core.messages import ToolMessage
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def extract_tool_output(agent_result: dict) -> tuple[str, str]:
    """
    Return (raw_tool_output, llm_summary) from an agent result.

    The agent message chain looks like:
        HumanMessage  →  AIMessage(tool_calls)  →  ToolMessage  →  AIMessage(summary)

    ToolMessage contains the raw output from the tool (titles + URLs + snippets).
    The final AIMessage is the LLM's prose summary which often drops URLs.
    We want BOTH: raw tool data for downstream agents, summary for display.
    """
    messages = agent_result["messages"]

    # Collect every ToolMessage — these hold the raw tool return values
    tool_outputs = [m.content for m in messages if isinstance(m, ToolMessage)]
    raw = "\n\n----\n\n".join(tool_outputs) if tool_outputs else ""

    # Last message is always the LLM's final prose reply
    summary = messages[-1].content if messages else ""

    # If the tool was never actually called, fall back to the LLM summary
    return (raw if raw else summary), summary


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ── Step 1 — Search Agent ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 1 — Search Agent is finding information ...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user",
            f"Search for recent and detailed information about: {topic}. "
            f"Make sure to call the web_search tool and return all titles, URLs, and snippets."
        )]
    })

    # Use the raw ToolMessage (has URLs) — not the LLM's summary (URLs stripped)
    state["search_results"], state["search_summary"] = extract_tool_output(search_result)

    print("\n📋 Raw Search Results (with URLs):\n", state["search_results"])
    print("\n💬 Agent Summary:\n", state["search_summary"])

    # ── Step 2 — Reader Agent ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 2 — Reader Agent is scraping top resource ...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    try:
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and call scrape_url on it to get deeper content.\n\n"
                f"Search Results (includes real URLs):\n{state['search_results'][:1200]}"
            )]
        })

        # Same fix: get raw scraped content from ToolMessage, not LLM summary
        state["scraped_content"], _ = extract_tool_output(reader_result)
        if not state["scraped_content"].strip():
            state["scraped_content"] = reader_result["messages"][-1].content

    except Exception as e:
        print(f"\n[WARNING] Reader agent failed: {e}")
        state["scraped_content"] = "(Scraping unavailable — using search results only.)"

    print("\nScraped Content:\n", state["scraped_content"])

    # ── Step 3 — Writer Chain ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 3 — Writer is drafting the report ...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS (with source URLs):\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    })

    print("\nFinal Report:\n", state["report"])

    # ── Step 4 — Critic Chain ─────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Step 4 — Critic is reviewing the report ...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCritic Feedback:\n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)