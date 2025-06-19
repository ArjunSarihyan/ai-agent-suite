import sys
import os
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
import streamlit as st

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crew import Adalchemy_v2

st.set_page_config(page_title="🧠 Adalchemy CrewAI", layout="centered")
st.title("🔍 Adalchemy CrewAI Interactive Tool")
st.markdown("Run taxonomy segmentation pipeline directly from UI.")

# Parse markdown table and extract average confidence
def parse_markdown_report(content: str):
    table_regex = re.compile(
        r"(\|.+\|)\n(\|[-\s|:]+\|)(\n(\|.*\|))+",
        re.MULTILINE
    )
    match = table_regex.search(content)
    if not match:
        return None, content, None

    table_block = match.group(0)
    parts = content.split(table_block)
    before_table = parts[0].strip()
    after_table = parts[1].strip() if len(parts) > 1 else ""

    # Extract average confidence
    avg_score_match = re.search(r'average confidence.*?([0-9]+\.[0-9]+)', content, re.IGNORECASE)
    avg_score = float(avg_score_match.group(1)) if avg_score_match else None

    lines = table_block.strip().splitlines()
    header_line = lines[0]
    data_lines = lines[2:]  # skip header and separator

    headers = [col.strip() for col in header_line.strip().split('|') if col.strip()]
    parsed_rows = []
    for line in data_lines:
        row = [col.strip() for col in re.split(r'(?<!\\)\|', line.strip())[1:-1]]
        if len(row) == len(headers):
            parsed_rows.append(row)
        elif len(row) > len(headers):
            row = row[:2] + [' | '.join(row[2:-2])] + row[-2:]
            parsed_rows.append(row)

    df = pd.DataFrame(parsed_rows, columns=headers)
    return df, before_table + "\n\n" + after_table, avg_score

# Color-coded score display
def render_avg_score(score: float):
    color = "#FF4B4B"  # Red
    if score >= 0.9:
        color = "#007F00"  # Dark Green
    elif score >= 0.8:
        color = "#4CAF50"  # Light Green
    elif score >= 0.7:
        color = "#FFB700"  # Yellow

    st.markdown(
        f"""
        <div style="font-size: 1.25em; margin-bottom: 1em;">
            <strong>Overall Quality Assessment Score:</strong>
            <span style="color: {color}; font-weight: bold;">{score:.2f}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Table styling with confidence coloring + hover
def style_dataframe_as_html(df: pd.DataFrame, threshold: float = 0.7) -> str:
    html = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2em;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 0.5em;
            text-align: left;
        }
        .low-score {
            color: red;
            font-weight: bold;
        }
        .tooltip {
            cursor: help;
            text-decoration: underline dotted;
        }
    </style>
    <table>
        <thead><tr>""" + "".join(f"<th>{col}</th>" for col in df.columns) + "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for i, value in enumerate(row):
            col_name = df.columns[i].lower()
            if col_name == "confidence score":
                try:
                    score = float(value)
                    cell = f'<td class="low-score">{value}</td>' if score < threshold else f"<td>{value}</td>"
                except ValueError:
                    cell = f"<td>{value}</td>"
            elif col_name == "evaluation notes":
                cell = f'<td><span class="tooltip" title="{value}">Hover to view</span></td>'
            else:
                cell = f"<td>{value}</td>"
            html += cell
        html += "</tr>"
    html += "</tbody></table>"
    return html

# UI form
with st.form("crew_form"):
    url = st.text_input("📎 Enter content URL", value="https://sports.yahoo.com")
    topic = st.text_area("🧠 Strategic Topic", value="Achieve a 20% growth in unique audience reach during Q2...")
    submitted = st.form_submit_button("Run CrewAI")

if submitted:
    st.info("⏳ Running Crew... Please wait.")
    inputs = {
        "url": url,
        "topic": topic,
        "current_year": str(datetime.now().year)
    }

    try:
        crew_model = Adalchemy_v2()
        result = crew_model.run_and_return_results(inputs=inputs)
        report_path = result.get("report_path")

        if report_path and Path(report_path).exists():
            st.success("✅ Crew Execution Completed!")
            with open(report_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            df, rest_of_report, avg_score = parse_markdown_report(markdown_content)

            if avg_score is not None:
                render_avg_score(avg_score)

            if df is not None:
                html_table = style_dataframe_as_html(df)
                st.markdown("### 📊 Scored Taxonomy Table")
                st.markdown(html_table, unsafe_allow_html=True)

            if rest_of_report:
                st.markdown("### 📘 Additional Report Summary")
                st.markdown(rest_of_report, unsafe_allow_html=True)

        else:
            st.warning("⚠️ Report file not found after crew execution.")
    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
