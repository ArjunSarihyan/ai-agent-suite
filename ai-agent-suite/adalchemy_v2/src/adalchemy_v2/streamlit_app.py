import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from datetime import datetime
from crew import Adalchemy_v2  # import directly from crew.py sibling

st.set_page_config(page_title="🧠 Adalchemy CrewAI", layout="centered")

st.title("🔍 Adalchemy CrewAI Interactive Tool")
st.markdown("Run taxonomy segmentation pipeline directly from UI.")

with st.form("crew_form"):
    url = st.text_input("📎 Enter content URL", value="https://sports.yahoo.com/nba/...")
    topic = st.text_area("🧠 Strategic Topic", value="Achieve a 20% growth in unique audience reach...")
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
        results_df = crew_model.run_and_return_results(inputs=inputs)

        st.success("✅ Crew Execution Completed!")

        if not results_df.empty:
            st.subheader("📊 Filtered Taxonomy Results")
            st.dataframe(results_df)

            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download as CSV", data=csv, file_name="taxonomy_results.csv", mime="text/csv")
        else:
            st.warning("No matches found after filtering.")

    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
