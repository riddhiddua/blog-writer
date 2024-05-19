import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Set your Google Generative AI API key
genai.configure(api_key=os.getenv("API_KEY")) 

# Model configuration (as provided in your example)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)


def generate_blog(topic, keywords, number_of_keywords, tone):
    """Generates a blog post using Google Gemini."""
    prompt_parts = [
        f'''As a blog-writer, and an expert in SEO
Follow the Instructions:
Step-1 : Write a short, engaging blog of {number_of_keywords} Words on the topic: {topic}. Keep the tone {tone}.
Step-2: Make sure to incorporate these keywords: {keywords}, to make it SEO-optimized and targeted.If 'keywords' are not present use relevant, SEO-optimized, targeted 'keywords' to the 'topic' 
Step-3: Output should be in a manner that it can be used directly as a published blog'''
    ]
    response = model.generate_content(prompt_parts)
    return response.text


def get_keywords_from_ai(topic):
    """Gets SEO keywords using Google Gemini."""
    prompt = f"""
    As an expert blog writer, specialized in SEO. Follow the below instructions to give the user SEO-optimized keywords.
    Instructions:
    Step-1: Understand the "Topic": {topic}
    Step-2: Suggest 10 relevant, SEO-optimized, targeted keywords for the title.
    Step-3: Format the keywords according to their ranking and then provide the answer in structured JSON, it should have 3 attributes:
    'keyword': relevant keyword
    'ranking': their ranking in the list of keywords
    'Avg. monthly Search': average monthly search of that keyword
    
    You can use Google Keyword Planner for better results
    """
    response = model.generate_content([prompt])
    return response.text  # Process the JSON output here


st.title("Blog-Writer")

col1, col2 = st.columns(2)

with col1:
    topic = st.text_input("Topic:")
    keywords = st.text_input("Keywords (comma-separated):")
    number_of_keywords = st.slider("Number of Words:",0, 1000, 500)
    tone = st.selectbox("Tone:", ["Formal","Conversational", "Informative","Persuasive","Humorous","Inspirational","Sarcastic","Empathetic"])

    submit_button = st.button("Generate Blog")
    ai_keywords_button = st.button("Search Keywords in AI")

with col2:
    st.markdown(
        f"[Google Keyword Planner](https://ads.google.com/aw/keywordplanner/home?ocid=6569447985&euid=1165942535&__u=2028387215&uscid=6569447985&__c=7666764265&authuser=0&sf=kp&subid=in-en-awhp-g-aw-c-t-kwp-hero%21o2)"
    )
    uploaded_file = st.file_uploader(
        "Upload Google Keyword Planner results (CSV)", type="csv"
    )
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='utf_16', skiprows=2, sep='\t')
        df = df.sort_values(
            by="Avg. monthly searches", ascending=False
        )  # Assuming column name
        top_keywords = df["Keyword"].head(10).tolist()
        keywords = ",".join(top_keywords)  # Populate keywords input

        if st.button("Submit"):
            blog_post = generate_blog(topic, top_keywords, number_of_keywords, tone)
            st.write(blog_post)

if submit_button:
    keyword_list = [kw.strip() for kw in keywords.split(",")]
    blog_post = generate_blog(topic, keyword_list,  number_of_keywords, tone)
    st.write(blog_post)

if ai_keywords_button:
    json_keywords = get_keywords_from_ai(topic)
    st.write(json_keywords)  # Display the JSON response
    # TODO: Parse the JSON and populate the keyword input box
