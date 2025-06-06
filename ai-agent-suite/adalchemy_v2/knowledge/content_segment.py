from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from pydantic import Field
from typing import Dict, Any
import pandas as pd
import json
from pathlib import Path

class ContentSegmentKnowledgeSource(BaseKnowledgeSource):
    """Loader that chunks content taxonomy TSV for CrewAI context."""

    repo_root: Path = Path(__file__).resolve().parents[1]

    file_path: Path = Field(
        default=repo_root / "Content Taxonomy 3.1.tsv",
        description="Path to the content taxonomy TSV file"
    )

    content: Dict[Any, str] = Field(default_factory=dict)

    @property
    def _output_dir(self) -> Path:
        root_path = Path(__file__).resolve().parents[1]
        output_dir = root_path / "knowledge" /"content_segment"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def load_content(self) -> Dict[Any, str]:
        try:
            # Load the TSV with tab separator, skip first row if it is header metadata
            df = pd.read_csv(self.file_path, sep="\t", dtype=str, skiprows=1).fillna("")
            df.columns = df.columns.str.strip()

            print(f"[DEBUG] Columns found in TSV: {list(df.columns)}")

            chunks = {}

            for _, row in df.iterrows():
                uid = row.get("Unique ID", "")
                if not uid:
                    continue  # skip rows without a UID

                segment = {
                    "Unique ID": uid,
                    "Parent ID": row.get("Parent", ""),
                    "Name": row.get("Name", ""),
                    "Tier 1": row.get("Tier 1", ""),
                    "Tier 2": row.get("Tier 2", ""),
                    "Tier 3": row.get("Tier 3", ""),
                    "Tier 4": row.get("Tier 4", ""),
                    "Extension": row.get("Extension", ""),
                }

                chunk_path = self._output_dir / f"{uid}.json"
                with open(chunk_path, "w", encoding="utf-8") as f:
                    json.dump(segment, f, indent=2)

                chunks[uid] = self._format(segment)

            print(f"[DEBUG] Created {len(chunks)} content taxonomy chunks.")
            self.content = chunks  # store for external access
            return chunks

        except Exception as e:
            raise ValueError(f"[ERROR] Failed to load and chunk TSV: {str(e)}")

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
            f"Hierarchy: {segment['Tier 1']} > {segment['Tier 2']} > "
            f"{segment['Tier 3']} > {segment['Tier 4']}\n"
            f"Extension: {segment.get('Extension', '')}"
        )
