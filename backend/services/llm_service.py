"""LLM service for content generation - connects to LM Studio local model via OpenAI-compatible API, with template fallback when LM Studio is unreachable."""
import os
import logging
import urllib.parse
from typing import Optional

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

LM_STUDIO_BASE_URL: str = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL: str = os.getenv("LM_STUDIO_MODEL", "")

_ALLOWED_HOSTS: frozenset[str] = frozenset({"localhost", "127.0.0.1", "::1"})

_client: Optional[OpenAI] = None
_resolved_model: str = ""


def _normalize_base_url(url: str) -> str:
    """Ensure *url* ends with ``/v1`` so the OpenAI client hits the correct LM Studio path."""
    url = url.rstrip("/")
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url


def _validate_lm_studio_url(url: str) -> None:
    """Raise ``ValueError`` if *url* does not point to a loopback address."""
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ""
    if host not in _ALLOWED_HOSTS:
        raise ValueError(
            f"LM Studio URL host '{host}' is not allowed. "
            "Only localhost / 127.0.0.1 / ::1 are permitted."
        )


def get_client() -> OpenAI:
    """Return a lazily-created OpenAI client pointed at LM Studio."""
    global _client
    if _client is None:
        base = _normalize_base_url(LM_STUDIO_BASE_URL)
        logger.debug("Creating OpenAI client → base_url=%s", base)
        _client = OpenAI(base_url=base, api_key="lm-studio")
    return _client


def get_model() -> str:
    """Return the configured or auto-detected model name."""
    global _resolved_model
    if _resolved_model:
        return _resolved_model
    if LM_STUDIO_MODEL:
        _resolved_model = LM_STUDIO_MODEL
        logger.debug("Using model from LM_STUDIO_MODEL env: %s", _resolved_model)
        return _resolved_model
    # Auto-detect: pick the first model exposed by LM Studio
    logger.debug("No model configured – fetching available models from LM Studio…")
    client = get_client()
    models = client.models.list()
    model_ids = [m.id for m in models.data]
    logger.debug("Models returned by LM Studio: %s", model_ids)
    if not model_ids:
        raise RuntimeError("LM Studio returned no available models.")
    _resolved_model = model_ids[0]
    logger.info("Auto-selected model: %s", _resolved_model)
    return _resolved_model


async def check_lm_studio_status() -> dict:
    """Check whether LM Studio is currently reachable. Returns a status dict."""
    health_url = _normalize_base_url(LM_STUDIO_BASE_URL) + "/models"
    try:
        async with httpx.AsyncClient(timeout=5.0) as http:
            resp = await http.get(health_url)
            resp.raise_for_status()
        return {"lm_studio": "online", "base_url": LM_STUDIO_BASE_URL}
    except Exception as exc:
        return {"lm_studio": "offline", "error": str(exc)}


async def generate_section(
    section_type: str,
    section_name: str,
    rqs_content: Optional[str],
    glossary_content: Optional[str],
    additional_context: str = "",
) -> str:
    """Generate markdown content for a section using LM Studio or template fallback."""

    system_prompt = (
        "You are an expert academic writer. Generate well-structured Markdown content "
        "for the requested paper section. Ensure strict adherence to the provided "
        "Research Questions (RQs) and use only terminology defined in the Glossary."
    )

    user_prompt = _build_generation_prompt(
        section_type, section_name, rqs_content, glossary_content, additional_context
    )

    # Validate the configured URL before attempting a call
    try:
        _validate_lm_studio_url(LM_STUDIO_BASE_URL)
    except ValueError:
        logger.warning("LM Studio URL validation failed – using template fallback")
        return _template_fallback(section_type, section_name, rqs_content, glossary_content)

    try:
        client = get_client()
        model = get_model()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        logger.warning("LM Studio call failed (%s) – using template fallback", exc)
        return _template_fallback(section_type, section_name, rqs_content, glossary_content)


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
    """Return a structured template when LM Studio is unreachable."""
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
