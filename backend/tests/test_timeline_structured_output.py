import json

from backend.pipeline.step2_timeline import TimelineExtractor


class OllamaTimelineManager:
    """Small fake for Ollama's external schema-constrained response boundary."""

    def get_current_provider_info(self):
        return {"provider": "ollama"}

    def call_with_retry(self, _prompt, _input_data, _max_retries=3, **kwargs):
        response_format = kwargs.get("response_format") or {}
        if response_format.get("type") != "json_schema":
            return "A prose summary that cannot become a timeline."
        item_properties = (
            response_format["json_schema"]["schema"]["properties"]["items"]
            ["items"]["properties"]
        )
        timestamp_pattern = r"^\d{2}:\d{2}:\d{2},\d{3}$"
        if (
            item_properties["start_time"].get("pattern") != timestamp_pattern
            or item_properties["end_time"].get("pattern") != timestamp_pattern
        ):
            return json.dumps(
                {
                    "items": [
                        {
                            "outline": "Useful workflow lesson",
                            "content": ["Start from user friction"],
                            "start_time": "Start from the first sentence",
                            "end_time": ":00:39,000",
                        }
                    ]
                }
            )
        return json.dumps(
            {
                "items": [
                    {
                        "outline": "Useful workflow lesson",
                        "content": ["Start from user friction"],
                        "start_time": "00:00:01,000",
                        "end_time": "00:00:39,000",
                    }
                ]
            }
        )


def test_ollama_timeline_schema_constrains_srt_timestamps(tmp_path):
    prompt_path = tmp_path / "timeline.txt"
    prompt_path.write_text("Return the timeline as JSON.", encoding="utf-8")
    srt_dir = tmp_path / "step1_srt_chunks"
    srt_dir.mkdir()
    (srt_dir / "chunk_0.json").write_text(
        json.dumps(
            [
                {
                    "index": 1,
                    "start_time": "00:00:00,000",
                    "end_time": "00:00:40,000",
                    "text": "Start from user friction before choosing technology.",
                }
            ]
        ),
        encoding="utf-8",
    )
    extractor = TimelineExtractor(
        metadata_dir=tmp_path,
        prompt_files={"timeline": str(prompt_path)},
    )
    extractor.llm_client.llm_manager = OllamaTimelineManager()

    result = extractor.extract_timeline(
        [
            {
                "title": "Useful workflow lesson",
                "subtopics": ["Start from user friction"],
                "chunk_index": 0,
            }
        ]
    )

    assert len(result) == 1
    assert result[0]["outline"] == "Useful workflow lesson"
    assert result[0]["start_time"] == "00:00:00,000"
    assert result[0]["end_time"] == "00:00:40,000"
