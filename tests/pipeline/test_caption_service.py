import math

import pytest

from src.pipeline.services.caption_service import CaptionService


@pytest.fixture
def caption_service():
    return CaptionService(
        min_segment_duration=1.8,
        final_segment_min_duration=0.5,
    )


def test_build_captions_distributes_durations(caption_service):
    text = "Hook. Body sentence one. Body sentence two."
    audio_duration = 12.0

    captions = caption_service.build_captions(text, audio_duration)

    assert len(captions) == 3
    assert captions[0]["text"].startswith("Hook")
    assert captions[-1]["text"].startswith("Body sentence two")

    # Somatório das durações deve respeitar o áudio (pequena tolerância).
    total = sum(round(item["end_time"] - item["start_time"], 2) for item in captions)
    assert math.isclose(total, audio_duration, rel_tol=0.05)


def test_build_captions_handles_empty_text(caption_service):
    captions = caption_service.build_captions("", 10.0)
    assert captions == []


def test_build_captions_handles_short_audio(caption_service):
    text = "Just one sentence."
    captions = caption_service.build_captions(text, 1.0)
    assert len(captions) == 1
    assert captions[0]["end_time"] <= 1.0
