import pytest

from src.pipeline.services.broll_query_service import BrollQueryService


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLMClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise RuntimeError("No response configured")
        return FakeResponse(self.responses.pop(0))


def test_generate_queries_from_json_response():
    client = FakeLLMClient(['["octopus hunting", "reef stealth", "underwater camouflage"]'])
    service = BrollQueryService(client)

    queries = service.generate_queries("Octopus story")

    assert queries == ["octopus hunting", "reef stealth", "underwater camouflage"]
    assert len(client.calls) == 1


def test_generate_queries_fallback_to_lines():
    raw_text = "- octopus facts\n- ocean secrets\n"
    client = FakeLLMClient([raw_text])
    service = BrollQueryService(client)

    queries = service.generate_queries("Anything")

    assert queries == ["octopus facts", "ocean secrets"]


def test_generate_queries_handles_errors():
    client = FakeLLMClient([])
    service = BrollQueryService(client)

    queries = service.generate_queries("content")

    assert queries == []
