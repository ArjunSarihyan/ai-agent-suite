import os
import re
import duckdb
from crewai.tools import BaseTool
from pydantic import BaseModel

class DuckDBToolSchema(BaseModel):
    query: str

class DuckDBTool(BaseTool):
    name: str = "nl2sql_tool"
    description: str = (
        "Executes SQL queries on taxonomy.db across adproduct, audience, and content tables "
        "using consistent ILIKE filters and saves results in result.md"
    )
    args_schema = DuckDBToolSchema

    def _extract_ilike_keywords(self, query: str):
        pattern = r"condensed_name_full\s+ILIKE\s+'%([^%']+)%'"
        return re.findall(pattern, query, flags=re.IGNORECASE)

    def _build_standard_query(self, table: str, keywords: list[str]):
        conditions = " OR ".join(
            [f"condensed_name_full ILIKE '%{kw.strip()}%'" for kw in keywords]
        )
        return f"SELECT * FROM {table} WHERE {conditions};"

    def _execute_query_and_format(self, cursor, query, table_name):
        try:
            results = cursor.execute(query).fetchall()
            columns = [desc[0] for desc in cursor.description]
            if not results:
                return f"### Table: {table_name}\nNo results found.\n\n"

            md_table = f"### Table: {table_name}\n\n"
            md_table += "| " + " | ".join(columns) + " |\n"
            md_table += "| " + " | ".join(["---"] * len(columns)) + " |\n"
            for row in results:
                md_table += "| " + " | ".join(str(cell) if cell is not None else "" for cell in row) + " |\n"
            md_table += "\n"
            return md_table
        except Exception as e:
            return f"### Table: {table_name}\nQuery failed: {e}\n\n"

    def _run(self, query: str) -> str:
        # Dynamically resolve path to taxonomy.db inside the knowledge folder
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        db_path = os.path.join(base_dir, "knowledge", "taxonomy.db")
        result_file = os.path.join(base_dir, "result.md")

        if not os.path.isfile(db_path):
            return f"❌ Database not found at {db_path}"

        # Extract keywords from the original query
        keywords = self._extract_ilike_keywords(query)
        if not keywords:
            return "❌ No valid ILIKE keywords found in the input query."

        with duckdb.connect(database=db_path, read_only=True) as con:
            output = "# Query Results\n\n"
            output += "## Query:\n```sql\n" + query.strip() + "\n```\n\n"

            for table in ["adproduct", "audience", "content"]:
                rewritten_query = self._build_standard_query(table, keywords)
                result = self._execute_query_and_format(con, rewritten_query, table)
                output += result

        with open(result_file, "w", encoding="utf-8") as f:
            f.write(output)

        return "✅ Query executed and result.md updated."

# Instantiate the tool for usage by the agent
nl2sql_tool = DuckDBTool()