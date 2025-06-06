from pathlib import Path
import pandas as pd
import json
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from pydantic import Field
from typing import Dict, Any

class AdProductSegmentKnowledgeSource(BaseKnowledgeSource):
    # Set repo root assuming this file is in knowledge/
    repo_root: Path = Path(__file__).resolve().parents[1]

    file_path: Path = Field(
        default=repo_root / "Ad Product Taxonomy 2.0.tsv",
        description="Path to the Ad Product Taxonomy TSV file"
    )

    content: Dict[Any, str] = Field(default_factory=dict)

    @property
    def _output_dir(self) -> Path:
        output_dir = self.repo_root / "knowledge" / "adproduct_segment"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def load_content(self) -> Dict[Any, str]:
        try:
            df = pd.read_csv(self.file_path, sep="\t", dtype=str).fillna("")
            chunks = {}

            for _, row in df.iterrows():
                uid = row.get("Unique ID", "")
                if not uid:
                    continue

                segment = {
                    "Unique ID": uid,
                    "Parent ID": row.get("Parent ID", ""),
                    "Name": row.get("Name", ""),
                    "Tier 1": row.get("Tier 1", ""),
                    "Tier 2": row.get("Tier 2", ""),
                    "Tier 3": row.get("Tier 3", ""),
                    "Extension Notes": row.get("Extension Notes", "")
                }

                chunk_path = self._output_dir / f"{uid}.json"
                with open(chunk_path, "w", encoding="utf-8") as f:
                    json.dump(segment, f, indent=2)

                chunks[uid] = self._format(segment)

            print(f"[DEBUG] Created {len(chunks)} ad product taxonomy chunks.")
            self.content = chunks
            return chunks

        except Exception as e:
            raise ValueError(f"[ERROR] Failed to load and chunk Ad Product TSV: {str(e)}")

    def validate_content(self, content: Any) -> str:
        return str(content)

    def add(self) -> None:
        content = self.load_content()
        for _, chunk in content.items():
            self.chunks.append(chunk)
        self._save_documents()

    def _format(self, segment: dict) -> str:
        return (
            f"UID: {segment['Unique ID']}\n"
            f"Parent ID: {segment['Parent ID']}\n"
            f"Name: {segment['Name']}\n"
            f"Hierarchy: {segment['Tier 1']} > {segment['Tier 2']} > {segment['Tier 3']}\n"
            f"Notes: {segment.get('Extension Notes', '')}"
        )
