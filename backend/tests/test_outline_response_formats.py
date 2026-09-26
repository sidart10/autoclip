import json

from backend.pipeline.step1_outline import OutlineExtractor


def test_outline_parser_accepts_category_prompt_json(tmp_path):
    prompt_path = tmp_path / "outline.txt"
    prompt_path.write_text("Return an outline.", encoding="utf-8")
    extractor = OutlineExtractor(
        metadata_dir=tmp_path,
        prompt_files={"outline": str(prompt_path)},
    )
    response = json.dumps(
        [
            {
                "title": "Decorating the boots",
                "subtopics": ["Choosing charms", "Applying glue"],
            }
        ]
    )

    result = extractor._parse_outline_response(response, chunk_index=2)

    assert result == [
        {
            "title": "Decorating the boots",
            "subtopics": ["Choosing charms", "Applying glue"],
            "chunk_index": 2,
        }
    ]
