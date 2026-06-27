from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

# ── Models ────────────────────────────────────────────────────────────────────
# Agents need reliable function/tool calling → use a larger, capable model.
# llama-3.1-8b-instant is too small: it generates <function=name>{} XML syntax
# instead of proper JSON tool calls, causing Groq to return 400 tool_use_failed.
agent_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Writer & Critic chains do pure text generation (no tools) → fast small model is fine.
chain_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)


# ── Agents ────────────────────────────────────────────────────────────────────
def build_search_agent():
    """Agent that calls web_search to find recent, reliable sources."""
    return create_agent(
        model=agent_llm,
        tools=[web_search],
    )


def build_reader_agent():
    """Agent that calls scrape_url to extract deep content from a page."""
    return create_agent(
        model=agent_llm,
        tools=[scrape_url],
    )


# ── Writer Chain ──────────────────────────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | chain_llm | StrOutputParser()


# ── Critic Chain ──────────────────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | chain_llm | StrOutputParser()