from io import BytesIO
from openai import OpenAI
import streamlit as st
import pandas as pd
from docx import Document

## Env
test_key = st.secrets["my_secrets"]["api_key"]

## Data
df = pd.read_excel("data_cleaned.xlsx", index_col=1)
print(len(df.columns))
options = list(df.index.values)

## Asset manager prompts ##
def firm_description_general(firm_name: str) -> str:
    return f'Give me a 5-10 sentence firm overview of {firm_name}. Be concise, and use bullet points'

def brief_history(firm_name: str) -> str:
    return f"Can you please provide a brief, concise history of the {firm_name} in bullet point form. Don't give a greeting"

def primary_offerings(firm_name: str)-> str:
    return f"What are the primary offerings of {firm_name}? Please provide a concise response in bullet point form"

def firm_size(firm_name: str) -> str:
    return f"What is the size of {firm_name}? Please provide a concise response in bullet point form"


## Open AI Setup ##

def createClient(api_key) -> OpenAI:
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

# Given a prompt, send to OpenAI and parse response
def query_openai(prompt: str, client: OpenAI, model_spec: str) -> str:
    completion = client.chat.completions.create(
        model=model_spec,
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

client = createClient(test_key)

def wrap(prompt: str) -> str:
    return query_openai(prompt, client, "sonar-pro")


## Download Processing ##
 # Generate DOCX and provide download button
def generate_docx(data: dict, user_input: str) -> BytesIO:
    doc = Document()
    doc.add_heading(f"RIA Report: {user_input}", level=1)

    for key, value in data.items():
        doc.add_heading(key.capitalize(), level=2)
        doc.add_paragraph(value)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Function to convert a dictionary to Excel in-memory
def to_excel(a_dict) -> BytesIO:
    a_df = pd.DataFrame(a_dict, index=[0])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        a_df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

## Web App ##
st.title("RIA Reports")

# Password input
password = st.text_input("Enter password", type="password")

# User input for the firm name
user_input = st.selectbox("Enter firm name:", options)


# Initialize data accumulator
data_acc = {}

# Handle report generation logic
if st.button("Generate RIA report"):

    # Add section for SEC data
    st.subheader("Reported SEC Data")

    st.markdown(f"**Home office location:** {df.at[user_input, 'Main Office City']}, {df.at[user_input, 'Main Office Country']}")
    st.markdown(f"**Discretionary AUM:** {df.at[user_input, "Discretionary AUM"]}")
    st.markdown(f"**Non-Discretionary AUM:** {df.at[user_input, "Non-Discretionary AUM"]}")
    st.markdown(f"**Total AUM:** {df.at[user_input, "Total AUM"]}")


    # Add a section heading
    st.subheader("Firm Research: AI Generated")

    # Validate password
    if password == st.secrets['my_secrets']['password']:
        if user_input:
            # Firm Overview
            data_acc['overview'] = wrap(firm_description_general(user_input))
            st.text_area("Firm Overview: AI GENERATED", data_acc['overview'], height=300)

            # Brief History
            data_acc['history'] = wrap(brief_history(user_input))
            st.text_area("History: AI GENERATED", data_acc['history'], height=300)

            # Primary Offerings
            data_acc['offerings'] = wrap(primary_offerings(user_input))
            st.text_area("Primary Offerings: AI GENERATED", data_acc['offerings'], height=300)

            # Firm Size
            data_acc['size'] = wrap(firm_size(user_input))
            st.text_area("Firm Size: AI GENERATED", data_acc['size'], height=300)

            docx_buffer = generate_docx(data_acc, user_input)

            st.download_button(
                label="Download Report as DOCX",
                data=docx_buffer,
                file_name=f"{user_input}_RIA_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            st.download_button(
                label="Download Report as XLSX",
                data=to_excel(data_acc),
                file_name=f"{user_input}_RIA_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("Please enter a firm name to generate the report.")
    else:
        st.error("Incorrect password. Please try again.")
