import torch
import streamlit as st
from api import analyse_news

torch.classes.__path__ = []

st.title("News Analysis and Summarization")

company_name = st.text_input("Enter company name:")

if st.button("Analyze"):

    if company_name.strip():
        try:
            summary, audio_file = analyse_news(company_name)

            if summary:
                st.subheader("Summary:")
                st.write(summary)
            else:
                st.warning("No articles found for this company.")

            if audio_file:
                st.subheader("Summary audio in Hindi:")
                st.audio(audio_file, format="audio/mp3")
            else:
                st.warning("Audio file not found.")

        except Exception as e:
            st.error(f"An error occurred while analyzing news: {e}")

    else:
        st.warning("Please enter a company name.")
