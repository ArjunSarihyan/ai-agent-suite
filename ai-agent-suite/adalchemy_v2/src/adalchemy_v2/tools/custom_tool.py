# src/adalchemy_v2/tools/custom_tool.py
import logging
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup

# Configure logging at the module level (you can adjust level and format as needed)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class URLIngestInput(BaseModel):
    url: str = Field(..., description="The URL to scrape content from.")

class URLIngestTool(BaseTool):
    name: str = "URL Content Ingestor"
    description: str = "Fetches and parses webpage content from a given URL."
    args_schema: Type[BaseModel] = URLIngestInput

    def _run(self, url: str) -> str:
        logging.info(f"Starting URL ingest for {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            logging.info("Successfully fetched the URL")
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style tags
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=" ", strip=True)
            logging.info("Successfully parsed the URL content")
            return text[:30000]  # Limit to 30000 characters for brevity
        except Exception as e:
            logging.error(f"Error fetching URL content: {e}")
            return f"Error fetching URL content: {str(e)}"