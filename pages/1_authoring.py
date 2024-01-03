import streamlit as st
import pandas as pd
import sys
import os


sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convo_template import draft_persona

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def click_button():
    st.session_state.clicked = True

def assemble_prompt(name, persona, training_scenario, step1, step2, step3, step4, step5):
    prompt = f"""
    You are```{name}```. Your persona is ```{persona}```. ```{training_scenario}```.
    The conversation will follow the steps in the following order:
    First, ```{step1}```
    Second, ```{step2}```
    Third, ```{step3}```
    Fourth, ```{step4}```
    Fifth, ```{step5}```
    """
    return prompt

def assemble_output(prompt, convo_index, convo_type):
    output = pd.DataFrame(
        {'prompt': [prompt],
         'convo_index': [convo_index],
         'convo_type': [convo_type]
        })
    return output

st.set_page_config(
    page_title="Authoring",
    layout="wide"
)

tab1, tab2 = st.tabs(["Character Setup", "Training Setup"])

if 'clicked' not in st.session_state:
    st.session_state.clicked = False


with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.header("Character Setup")
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            name = st.text_input("Character Name")
            age = st.text_input("Age")
            race = st.text_input("Race & Ethnicity")
        with col1_2:
            occupation = st.text_input("Occupation")
            gender = st.text_input("Gender")

        persona = st.text_area("Character Persona")

    with col2:
        st.button("Auto-generate", on_click=click_button, key="generate")
        st.session_state.result = None
        if st.session_state.clicked:
            st.session_state.result = draft_persona(name, age, gender, occupation)
            st.write(st.session_state.result)
        persona = st.session_state.result

    st.download_button(
        label="Download",
        data=output.to_csv().encode('utf-8'),
        file_name='training_prompt.csv',
        mime = 'text/csv',
    )
