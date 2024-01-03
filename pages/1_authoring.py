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

        # if st.button("Auto-generate", key="generate"):
        #     persona = draft_persona(name, age, gender, occupation)
        # st.write(persona)


with tab2:
    st.header("Training Setup")
    col3_1, col3_2 = st.columns(2)
    with col3_1:
        training_scenario = st.text_area("Training Scenario")
        difficulty = st.selectbox("Difficulty level", ("Practice", "Application"))
        training_type = st.selectbox("Training Types", ("Full Conversation", "Skill Based", "Contextual"))

        if "Skill Based" in training_type:
            selected_skill = st.selectbox("The skill to be trained on", ("Acknowledging perspective", "Managing expectation",
                                                                  "Purposeful questioning", "Providing feedback"))
    with col3_2:
        st.markdown("Conversation Flow Setup")
        step1 = st.multiselect("Step 1: How to start the conversation?", ("Set the stage", "Ask a question to prompt reflection"))
        step2 = st.multiselect("Step 2: How to pave the conversation for coaching?", (
        "Acknowledging perspective", "Prompt for more questions to dig deeper",
        "None"))
        step3 = st.multiselect("Step 3: How to provide feedback?", (
        "Ask a question about the situation", "Ask a question about the behavior", "Ask a question about the impact",
        "Provide feedback on situation", "Provide feedback on behavior", "Provide feedback on impact"))
        step4 = st.multiselect("Step 4: How to provide resolution or next steps?", ("Ask questions to come up with resolutions", "Share possible resolutions to improve"))
        step5 = st.multiselect("Step 5: How to end the conversation?", ("Re-iterate on next steps", "None"))

with st.sidebar:
    st.header("Character and Training Scenario Setup")
    st.markdown('''
                Please create the character and training setup tabs to setup the soft skill training.  \n
                When you finish, please download the json file with the button below:''')
    prompt = assemble_prompt(name, persona, training_scenario, step1, step2, step3, step4, step5)
    
    output = assemble_output(prompt, convo_index, convo_type)
    


    st.download_button(
        label="Download",
        data=output.to_csv().encode('utf-8'),
        file_name='training_prompt.csv',
        mime = 'text/csv',
    )
