from unittest.mock import Mock

import pytest
import requests

from agent import run_agent


@pytest.fixture
def mock_dlq():
    return Mock()


def test_wikipedia_success_returns_answer(mock_dlq):
    mock_wikipedia = Mock(return_value="Morocco is located in North Africa.")

    result = run_agent("Where is Morocco?", mock_wikipedia, mock_dlq)

    assert result["status"] == "SUCCESS"
    assert "North Africa" in result["answer"]
    mock_dlq.assert_not_called()


def test_wikipedia_failure_redirects_to_dlq(mock_dlq):
    mock_wikipedia = Mock(side_effect=requests.Timeout("API timeout"))

    result = run_agent("Where is Morocco?", mock_wikipedia, mock_dlq)

    assert result["status"] == "FAILED_ROUTED_TO_DLQ"
    mock_dlq.assert_called_once_with("Where is Morocco?")


def test_network_errors_are_handled(mock_dlq):
    errors = [
        requests.ConnectionError("API unavailable"),
        requests.Timeout("API timeout"),
    ]

    for api_error in errors:
        mock_wikipedia = Mock(side_effect=api_error)
        result = run_agent("Python language", mock_wikipedia, mock_dlq)
        assert result["answer"] == "Service Wikipedia indisponible."


def test_empty_wikipedia_result_redirects_to_dlq(mock_dlq):
    mock_wikipedia = Mock(side_effect=ValueError("Aucun resultat"))

    result = run_agent("Unknown subject", mock_wikipedia, mock_dlq)

    assert result["status"] == "FAILED_ROUTED_TO_DLQ"
    mock_dlq.assert_called_once()


def test_unexpected_programming_error_is_not_hidden(mock_dlq):
    mock_wikipedia = Mock(side_effect=TypeError("Bug interne"))

    with pytest.raises(TypeError, match="Bug interne"):
        run_agent("Question", mock_wikipedia, mock_dlq)
