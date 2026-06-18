"""Follow-up extraction must not re-mine rejected values from the original query."""

from unittest.mock import MagicMock, patch

import pytest

from agent import extract_params_heuristic, load_registry, phase2_extract_params


@pytest.fixture
def analyze_api():
    registry = load_registry()
    return next(a for a in registry["apis"] if a["id"] == "analyze_agent_communication")


def test_heuristic_reextracts_connection_from_combined_text(analyze_api):
    """Regression: mining the original + follow-up line captures topic words."""
    out = extract_params_heuristic(
        "analyze agent connection\nnlp-dbactm-sp17",
        analyze_api,
        {"agent"},
        apply_confidence_filters=False,
    )
    assert out.get("agent") == "connection"


def test_followup_text_uses_only_supplemental_answers(analyze_api):
    with patch("agent.llm_extract") as mock_llm:
        mock_llm.invoke.return_value = MagicMock(content="{}")
        result = phase2_extract_params(
            "analyze agent connection",
            analyze_api,
            {},
            allowed_names={"agent"},
            apply_confidence_filters=False,
            followup_text="nlp-dbactm-sp17",
            latest_followup_line="nlp-dbactm-sp17",
        )
    assert result.get("agent") == "nlp-dbactm-sp17"


def test_first_pass_still_uses_original_query(analyze_api):
    with patch("agent.llm_extract") as mock_llm:
        mock_llm.invoke.return_value = MagicMock(content="{}")
        result = phase2_extract_params(
            "analyze agent connection",
            analyze_api,
            {},
            allowed_names={"agent"},
            apply_confidence_filters=True,
        )
    assert "agent" not in result
