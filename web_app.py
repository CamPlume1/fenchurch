from openai import OpenAI
import streamlit as st
from itertools import permutations

## Env
test_key = st.secrets["my_secrets"]["api_key"]

## Asset manager prompts ##
def firm_description_general(firm_name: str) -> str:
    return f'Give me a 5-10 sentence firm overview of {firm_name}. Be concise, and use bullet points'

def brief_history(firm_name: str) -> str:
    return f"Can you please provide a brief, concise history of the {firm_name} in bullet point form. Don't give a greeting"

def primary_offerings(firm_name: str)-> str:
    return f"What are the primary offerings of {firm_name}? Please provide a concise response in bullet point form"

def firm_size(firm_name: str) -> str:
    return f"What is the size of {firm_name}? Please provide a concise response in bullet point form"


## Open AI Setup

def createClient(api_key) -> OpenAI:
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

# Given a prompt, send to OpenAI and parse respose
def query_openai(prompt: str, client: OpenAI, model_spec: str) -> str:
    completion = client.chat.completions.create(
        model=model_spec,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


## Web App ##
client = createClient(test_key)

def wrap(prompt: str) -> str:
    return query_openai(prompt, client, "sonar-pro")

st.title("RIA Reports")

user_input = st.text_input("Enter text:")
if st.button("Generate RIA report"):

    # Firm Overview
    overview = wrap(firm_description_general(user_input))
    st.text_area(f"Firm Overview", overview, height=300)

    # Brief History
    history = wrap(brief_history(user_input))
    st.text_area(f"History", history, height=300)

    # Primary Offerings
    offerings = wrap(primary_offerings(user_input))
    st.text_area(f"Primary Offerings", offerings, height=300)



