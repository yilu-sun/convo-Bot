import openai
import os

from langchain.chains import LLMChain

from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)

from langchain.chat_models import ChatOpenAI

# Load environment variables
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')
llm = "gpt-3.5-turbo-1106" #"gpt-4-1106-preview"
randomness = 1

def check_hate_information(response):
    """
    this function double check whether a response contains hate word or speech
    :param response: information to be checked
    :return: True if contains hate information
    """
    # check for moderation
    moderation_response = openai.Moderation.create(
        input=response
    )
    print(moderation_response)
    moderation_output = moderation_response["results"][0]
    # if inappropriate response, manually close the conversation
    return True if (moderation_output['flagged']) else False

def get_completion(prompt, model=llm):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=randomness,
    )
    return response.choices[0].message["content"]

def check_user_strategy(response):
    prompt = f"""
    Your task is to classify ```{response}``` into one the following categories: "Interests", "Positive Expectations", "Proposal", "Concession", "Facts", "Procedural", "Power", "Rights".
    The output should be one of the following: "Interests", "Positive Expectations", "Proposal", "Concession", "Facts", "Procedural", "Power", "Rights".
    Interests is defined as reference to the wants, needs, or concerns of one or both parties. This may include questions about why the negotiator wants or feels the way they do. For example "We can figure this out. I understand that you’ve been really busy lately."
    Positive Expectations is defined as communicating positive expectations through the recognition of similarities and common goals. For example "I know you’re an excellent employee and I know you will improve in future."
    Proposal is defined as proposing concrete recommendations that may help resolve the conflict. For example, "Why don’t we record your progress weekly instead of monthly, so we can stay on track?" 
    Concession is defined as changing an initial view or position (in response to a proposal) to resolve a conflict. For example, "That makes sense, I’ll try recording my weekly progress instead of doing it monthly."
    Fact is defined as providing information on the situation or history of the dispute, including requests for information, clarification, or summaries. For example "I got a customer complaint that you rolled your eyes to them."
    Procedural is defined as introductory messages, including discussion about discussion topics, procedures, etc. For example, "Hi! How are you? I would like to have a coaching conversation."
    Power is defined as using threats and coercion to try to force the conversation into a resolution. For example, "I’m going to tell everyone you’ve been missing deadlines."
    Rights is defined as appealing to fixed norms and standards to guide a resolution. For example, "Sorry, I can’t do anything. Company policy doesn’t allow that."
    """
    return get_completion(prompt)


def check_coping_strategy(strategy):
    if strategy in ["Interests", "Positive Expectations", "Proposal", "Concession"]:
        return("You used a coorporative strategy, please keep using those strategies.")
    if strategy in ["Facts", "Procedural"]:
        return("You used a netural strategy, please continue to use those strategies or coorpative strategies.")
    else:
        return("You used a competitive strategy, please consider using netural or coorporative strategies.")



def draft_persona(name, age, gender, role):
    prompt = f"""
    Your task is to create a persona. 
    The name of the persona is ```{name}```.
    The age of the persona is ```{age}```.
    The gender of the persona is ```{gender}```.
    The occupation of the persona is ```{role}```.
    The persona will be a paragraph that includes the background, interests, goals, challenges and values. 
    """
    return get_completion(prompt)


