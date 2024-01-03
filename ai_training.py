import pandas as pd
import os
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI
from convo_template import check_hate_information, check_user_strategy, check_coping_strategy

from langchain.chains import LLMChain

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)


SAFETY_CHECK = True
llm = "gpt-3.5-turbo-1106" #"gpt-4-1106-preview"
provider = "openai"

st.header("Convo Bot")
st.markdown("Please upload the character and the training scenario to start the conversation")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'strategy' not in st.session_state:
    st.session_state['strategy'] = []

if 'safety' not in st.session_state:
    st.session_state['safety'] = []

if 'message_string' not in st.session_state:
    st.session_state['message_string'] = ''


user_prompt = "You are Ethan, a 28-year-old grocery store customer whose personality traits " \
              "and life factors shape his shopping behaviors and motivations. With high levels " \
              "of openness, Ethan is curious and eager to try new foods and flavors. He enjoys "\
              "exploring different cuisines and ingredients, seeking variety and culinary adventure. " \
              "His low conscientiousness makes him more flexible and spontaneous in his grocery shopping, "\
              "often relying on inspiration and impulse purchases rather than strict planning. "\
              "In addition to his personality traits, Ethan's motivations are influenced by various "\
              "life factors. One of his primary motivations is convenience. As a busy professional, " \
              "he values efficiency and seeks ready-to-eat or quick-to-prepare meals and snacks that " \
              "fit his on-the-go lifestyle. Ethan is also motivated by social connections. He enjoys " \
              "hosting gatherings and sharing meals with friends and family, making him inclined to "\
              "purchase ingredients for entertaining and creating memorable dining experiences. " \
              "Furthermore, Ethan's motivation is driven by affordability. He seeks cost-effective options, "\
              "comparing prices, and looking for deals to stretch his budget while still enjoying quality products."\
              "Overall, Ethan Sullivan is an open-minded, convenience-seeking, and budget-conscious grocery store customer. "\
              "His motivations center around exploring new tastes, accommodating his busy lifestyle, and nurturing his social "\
              "connections through food. He approaches his grocery shopping with a more relaxed and spontaneous mindset, embracing "\
              "culinary adventures and seeking value in his purchases. Ethan's inclination for variety and practicality makes him "\
              "an adaptable and motivated shopper within the grocery store setting."

response_container = st.container()

# User input

def save_message_string(verbose=False):
    human = st.session_state['past']
    ai = st.session_state['generated']
    strategy = st.session_state['strategy']
    safety = st.session_state['safety']
    convo_log = pd.DataFrame()
    human_response = []
    ai_response = []

    st.session_state['message_string'] = ""
    for h, a in zip(human, ai):
        st.session_state['message_string'] += f" \n\n HUMAN: {h}\n\n AI: {a}"
        human_response.append(h)
        ai_response.append(a)
    convo_log['learner_response'] = human_response
    convo_log['character_response'] = ai_response
    convo_log['strategy_used'] = strategy
    convo_log['safety'] = safety

    if verbose:
        st.write(st.session_state.message_string)
        st.write(st.session_state)

    return convo_log

def generate_response(prompt, system_instructions="", previous_messages="", provider="openai"):
    system_template = """
        {instructions}

        Previous messages in this conversation so far are: 
        {previous_messages}
        """

    system_prompt = SystemMessagePromptTemplate.from_template(system_template)

    human_template = "{anything}"
    human_prompt = HumanMessagePromptTemplate.from_template(human_template)
    prompt_template = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

    chain = LLMChain(llm=llm,
                     prompt=prompt_template)

    output = chain.run({"anything": prompt,
                        "instructions": system_instructions,
                        "previous_messages": previous_messages})

    return output

with st.sidebar:
    uploaded_files = st.file_uploader("Upload a CSV file", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        user_prompt = pd.read_csv(uploaded_file)['prompt'][0]
        st.write("filename:", uploaded_file.name)

    st.write("The current model used is GPT 3.5.")
    temperature = st.slider("Select conversation randomness", 0.0, 1.0, 0.7)

    llm = ChatOpenAI(model_name=llm, temperature=temperature, request_timeout=240)



input_container = st.container()
with input_container:
    user_input = st.text_area("You: ", "", key="input")


with response_container:
    if user_input:
        if SAFETY_CHECK and check_hate_information(user_input):
            st.error("No hateful speech, please respond again")

        else:
            user_strategy = check_user_strategy(user_input)
            st.info(user_strategy)
            st.warning(check_coping_strategy(user_strategy))
            response = generate_response(user_input,
                                         system_instructions=user_prompt,
                                         previous_messages=st.session_state.message_string,
                                         provider=provider)
            st.session_state.past.append(user_input)
            st.session_state.strategy.append(user_strategy)
            st.session_state.safety.append(check_hate_information(user_input))

            if SAFETY_CHECK and check_hate_information(response):
                st.session_state.generated.append("Ok let's try to pick this up at another time.")
            else:
                st.session_state.generated.append(response)

        save_message_string()
        

    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state['generated'][i], key=str(i))

with st.sidebar:
    convo_log_output = save_message_string()
    print(convo_log_output)
    st.download_button(
        label="Download Conversation",
        data=convo_log_output.to_csv().encode('utf-8'),
        file_name='conversation_log.csv',
        mime='text/csv'
    )