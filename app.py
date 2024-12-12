import streamlit as st
from streamlit_option_menu import option_menu
import re
from PyPDF2 import PdfReader
from textblob import TextBlob


# Function to extract text from a single page and find cited sentences
def extract_cited_sentences_from_text(text):
    cited_sentences = []
    cited_pattern = r"([^.]*\[(\d+)\][^.]*\.)|([^.]*\(\d{4}\)[^.]*\.)|([^.]*et al\.[^.]*\.)"
    matches = re.findall(cited_pattern, text)
    for match in matches:
        cited_sentences.append(''.join(match))  # Join all matched parts
    return cited_sentences


# Function to extract all cited sentences from the PDF
def extract_cited_sentences(pdf_file):
    reader = PdfReader(pdf_file)
    cited_sentences = []

    # Process each page individually
    for page in reader.pages:
        text = page.extract_text()
        if text:  # Skip empty pages
            cited_sentences += extract_cited_sentences_from_text(text)

    return cited_sentences


# Function to determine sentiment of a sentence
def get_sentiment(sentence):
    analysis = TextBlob(sentence)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "Positive", "green"
    elif polarity < 0:
        return "Negative", "red"
    else:
        return "Neutral", "yellow"


# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",  # Required
        options=["Home", "About", "Contact"],  # Required
        icons=["house", "info", "envelope"],  # Optional
        menu_icon="cast",  # Optional
        default_index=0,  # Optional
    )

# Main content based on selection
if selected == "Home":
    st.title("Welcome to the Home Page")
    st.write("This is the main content area for the Home page.")

    # Add PDF upload button
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Ensure sentences and sentiments are stored in session state
    if "cited_sentences" not in st.session_state:
        st.session_state["cited_sentences"] = []

    if "sentiments" not in st.session_state:
        st.session_state["sentiments"] = []

    if uploaded_file is not None:
        st.success("File uploaded successfully!")
        # Add a "Proceed" button
        if st.button("Proceed"):
            with st.spinner("Extracting cited sentences from the uploaded file..."):
                try:
                    # Extract cited sentences
                    cited_sentences = extract_cited_sentences(uploaded_file)

                    # Store sentences and reset sentiments in session state
                    st.session_state["cited_sentences"] = cited_sentences
                    st.session_state["sentiments"] = [None] * len(cited_sentences)

                    st.success("Cited sentences extracted successfully!")
                except Exception as e:
                    st.error(f"An error occurred while processing the file: {e}")

    # If cited sentences are available, display them
    if st.session_state["cited_sentences"]:
        st.subheader("Cited Sentences Found:")

        for idx, sentence in enumerate(st.session_state["cited_sentences"], start=1):
            with st.expander(f"Sentence {idx}"):
                st.markdown(f"**{idx}.** {sentence.strip()}")

                # Check if sentiment is already calculated
                if st.session_state["sentiments"][idx - 1] is not None:
                    sentiment, color = st.session_state["sentiments"][idx - 1]
                    st.markdown(f"**Sentiment:** <b style='color:{color}'>{sentiment}</b>", unsafe_allow_html=True)
                else:
                    # Button to calculate sentiment
                    if st.button(f"Show Sentiment for Sentence {idx}", key=f"show_{idx}"):
                        sentiment, color = get_sentiment(sentence.strip())
                        st.session_state["sentiments"][idx - 1] = (sentiment, color)
