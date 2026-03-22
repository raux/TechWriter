"""LLM service for content generation - uses a simple template-based approach when no LLM API key is configured, otherwise calls OpenAI-compatible API."""
import os
import httpx
from typing import Optional

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")


async def generate_section(
    section_type: str,
    section_name: str,
    rqs_content: Optional[str],
    glossary_content: Optional[str],
    additional_context: str = "",
) -> str:
    """Generate markdown content for a section using LLM or template fallback."""

    system_prompt = (
        "You are an expert academic writer. Generate well-structured Markdown content "
        "for the requested paper section. Ensure strict adherence to the provided "
        "Research Questions (RQs) and use only terminology defined in the Glossary."
    )

    user_prompt = _build_generation_prompt(
        section_type, section_name, rqs_content, glossary_content, additional_context
    )

    if not OPENAI_API_KEY:
        return _template_fallback(section_type, section_name, rqs_content, glossary_content)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OPENAI_API_BASE}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _build_generation_prompt(
    section_type: str,
    section_name: str,
    rqs_content: Optional[str],
    glossary_content: Optional[str],
    additional_context: str,
) -> str:
    parts = [f"Generate the **{section_type}** section titled '{section_name}' for an academic paper."]
    if rqs_content:
        parts.append(f"\n## Research Questions (RQs)\n{rqs_content}")
    if glossary_content:
        parts.append(f"\n## Glossary\n{glossary_content}")
    if additional_context:
        parts.append(f"\n## Additional Context\n{additional_context}")
    parts.append("\nOutput valid Markdown only. Do not include any preamble or explanation outside the Markdown.")
    return "\n".join(parts)


def _template_fallback(
    section_type: str,
    section_name: str,
    rqs_content: Optional[str],
    glossary_content: Optional[str],
) -> str:
    """Return a structured template when no LLM API key is configured."""
    templates = {
        "introduction": "# Introduction\n\n## Background\n\n[Provide background and motivation here.]\n\n## Problem Statement\n\n[State the problem this paper addresses.]\n\n## Contributions\n\n- Contribution 1\n- Contribution 2\n\n## Paper Structure\n\nThe remainder of this paper is organised as follows...",
        "data_preparation": "# Data Preparation\n\n## Dataset Description\n\n[Describe the dataset(s) used.]\n\n## Preprocessing Steps\n\n1. Step 1\n2. Step 2\n\n## Data Quality\n\n[Discuss data quality measures.]",
        "rqs": "# Research Questions\n\n## RQ1\n\n[State Research Question 1.]\n\n## RQ2\n\n[State Research Question 2.]\n\n## RQ3\n\n[State Research Question 3.]",
        "methodology": f"# Methodology\n\n## Overview\n\n[Provide methodology overview for {section_name}.]\n\n## Approach\n\n[Describe the approach in detail.]\n\n## Implementation\n\n[Describe implementation details.]",
        "results": f"# Results\n\n## Experimental Setup\n\n[Describe experimental setup for {section_name}.]\n\n## Quantitative Results\n\n| Metric | Value |\n|--------|-------|\n| Metric 1 | X |\n\n## Analysis\n\n[Analyse the results.]",
        "discussion": "# Discussion\n\n## Interpretation\n\n[Interpret the results in context of the RQs.]\n\n## Limitations\n\n[Discuss limitations.]\n\n## Future Work\n\n[Suggest future research directions.]",
        "related_work": "# Related Work\n\n## Category 1\n\n[Review related work in category 1.]\n\n## Category 2\n\n[Review related work in category 2.]\n\n## Comparison with Our Approach\n\n[Compare with our approach.]",
        "conclusion": "# Conclusion\n\n[Summarise the main findings and contributions.]\n\n## Summary of Contributions\n\n[List main contributions.]\n\n## Final Remarks\n\n[Closing remarks.]",
        "glossary": "# Glossary\n\n| Term | Definition |\n|------|------------|\n| Term 1 | Definition of term 1 |\n| Term 2 | Definition of term 2 |",
    }
    content = templates.get(section_type, f"# {section_name}\n\n[Content for {section_type} goes here.]")

    if rqs_content:
        content += f"\n\n<!-- Generated with RQs context: {len(rqs_content)} chars -->"
    if glossary_content:
        content += f"\n\n<!-- Generated with Glossary context: {len(glossary_content)} chars -->"

    return content
