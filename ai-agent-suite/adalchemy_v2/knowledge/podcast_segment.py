from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from pydantic import Field
from typing import Dict, Any
import pandas as pd
import json
from pathlib import Path

class PodcastSegmentKnowledgeSource(BaseKnowledgeSource):
    """Loader that chunks podcast genre mapping TSV for CrewAI context."""

    root_path: Path = Path(__file__).resolve().parents[1]

    file_path: Path = Field(
        default=root_path / "knowledge" / "Podcast Genre Mapping.tsv",
        description="Path to the podcast genre mapping TSV file"
    )
    content: Dict[Any, str] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        # Allow overriding file_path via kwargs, else use default Path object
        file_path = kwargs.get("file_path", self.file_path)
        kwargs["file_path"] = Path(file_path)
        super().__init__(**kwargs)

        print(f"[DEBUG] Using podcast genre mapping file at: {self.file_path}")
        print(f"[DEBUG] Chunks will be saved in: {self._output_dir}")

    @property
    def _output_dir(self) -> Path:
        output_dir = self.root_path / "knowledge" / "podcast_segment"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def load_content(self) -> Dict[Any, str]:
        try:
            df = pd.read_csv(self.file_path, sep="\t", dtype=str).fillna("")
            chunks = {}

            for _, row in df.iterrows():
                genre = row.get("Podcast Genres", "")
                unique_id = row.get("Content 3.1 Unique ID", "")

                if not unique_id:
                    continue  # Skip rows without unique ID

                segment = {
                    "Podcast Genres": genre,
                    "Content 3.1 Unique ID": unique_id,
                    "Content 3.1 Mapping": row.get("Content 3.1 Mapping", ""),
                }

                chunk_path = self._output_dir / f"{unique_id}.json"
                with open(chunk_path, "w", encoding="utf-8") as f:
                    json.dump(segment, f, indent=2)

                chunks[unique_id] = self._format(segment)

            print(f"[DEBUG] Created {len(chunks)} podcast genre chunks.")
            self.content = chunks
            return chunks

        except Exception as e:
            raise ValueError(f"[ERROR] Failed to load and chunk podcast TSV: {str(e)}")

    def validate_content(self, content: Any) -> str:
        return str(content)

    def add(self) -> None:
        content = self.load_content()
        for _, chunk in content.items():
            self.chunks.append(chunk)
        self._save_documents()

    def _format(self, segment: dict) -> str:
        return (
            f"Podcast Genre: {segment['Podcast Genres']}\n"
            f"Content 3.1 Unique ID: {segment['Content 3.1 Unique ID']}\n"
            f"Content 3.1 Mapping: {segment.get('Content 3.1 Mapping', '')}"
        )
