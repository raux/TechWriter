"""Consistency checking service - validates sections against RQs and checks cross-file terminology."""
import re
from typing import List, Dict, Optional

from backend.models import ConsistencyIssue

# Sections that are not expected to directly reference an RQ
SECTIONS_WITHOUT_RQ_REQUIREMENT = frozenset({
    "introduction",
    "related_work",
    "conclusion",
    "data_preparation",
    "glossary",
})


def extract_terms_from_glossary(glossary_content: str) -> Dict[str, str]:
    """Extract term->definition mapping from a Markdown glossary (table format)."""
    terms: Dict[str, str] = {}
    rows = re.findall(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", glossary_content)
    for term, definition in rows:
        term = term.strip()
        if term.lower() not in ("term", "---", ""):
            terms[term] = definition.strip()
    return terms


def check_terminology_consistency(
    sections: Dict[str, str],
    glossary_terms: Dict[str, str],
) -> List[ConsistencyIssue]:
    """
    Cross-file scan: detect if a term from the glossary is referenced by an alias
    (e.g., 'Algorithm A' used as 'Method A' in another section).

    Simple heuristic: find pairs of terms that appear in the same sentences differently.
    """
    issues: List[ConsistencyIssue] = []

    term_list = list(glossary_terms.keys())

    for section_name, content in sections.items():
        sentences = re.split(r"[.!?\n]", content)
        for sentence in sentences:
            found_terms = [t for t in term_list if re.search(rf"\b{re.escape(t)}\b", sentence, re.IGNORECASE)]
            if len(found_terms) >= 2:
                issues.append(
                    ConsistencyIssue(
                        term=", ".join(found_terms),
                        found_in=section_name,
                        context=sentence.strip()[:200],
                    )
                )

    return issues


def validate_section_against_rqs(
    section_content: str,
    rqs_content: str,
    introduction_content: Optional[str],
    section_name: str,
) -> List[str]:
    """
    Validate a section against the RQs and Introduction.
    Returns a list of issues/warnings.
    """
    issues: List[str] = []

    if not rqs_content:
        issues.append("No RQs node found. Cannot validate alignment with research questions.")
        return issues

    rq_refs = re.findall(r"\bRQ\d+\b", section_content, re.IGNORECASE)

    if not rq_refs and section_name not in SECTIONS_WITHOUT_RQ_REQUIREMENT:
        issues.append(
            f"Section '{section_name}' does not explicitly reference any Research Question (RQ1, RQ2, etc.). "
            "Ensure the section aligns with at least one defined RQ."
        )

    section_terms = set(re.findall(r"\*\*([^*]+)\*\*", section_content))
    prior_terms = set()
    if introduction_content:
        prior_terms.update(re.findall(r"\*\*([^*]+)\*\*", introduction_content))
    prior_terms.update(re.findall(r"\*\*([^*]+)\*\*", rqs_content))

    new_terms = section_terms - prior_terms
    if new_terms:
        issues.append(
            f"New terminology introduced in '{section_name}' not present in Introduction or RQs: "
            + ", ".join(f"**{t}**" for t in sorted(new_terms))
            + ". Consider adding these to the Glossary."
        )

    if "results" in section_name.lower():
        methodology_name = section_name.lower().replace("results", "methodology")
        issues.append(
            f"Reminder: Results section '{section_name}' requires a corresponding Methodology node. "
            f"Expected: '{methodology_name}' or similar."
        )

    return issues
