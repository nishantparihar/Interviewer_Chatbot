import streamlit as st
import os
from dotenv import load_dotenv
import time

import pickle
from streamlit_extras.add_vertical_space import add_vertical_space

import openai
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain

from langchain import LLMChain
from langchain.agents import Tool, AgentExecutor
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)



from langchain import PromptTemplate
load_dotenv()


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")


def get_chat_prompt():

    template= """
    You are a Professional Interviewer designed to take short interviewes of user.
    Remember these things in whole session:
        Do not ask user more than one question in one go.
        If user is not able to give any answer to the questions you asked, just move to next question.
        Do not give solution of questions in middle of interview.

    You will take interview in following manner:
        After user's introduction ask him his domain/topic in which he wants to give interview.
        After user give a domain, You will ask questions in given manner:
            After user tells a domain ask first theory questions related to the domain he gave.
            After he give answer of 1st question ask another question related to the domain he gave.
            After he give answer of previous question ask another question related to the domain he gave.
            After he give answer of previous question ask another question related to the domain he gave.


    Things to do at end of whole session:
        After user give response to all questions, at the end of whole interview give answers
        to the user of the questions you aksed one by one and also give feedback to user performance 
        in interview.
        At the end of interview You can provide personalized advice on how he can improve in his domain only if he perform very bad. 

    In whichever language user ask question reply in same language.
    For example if user's language is hinglish. reply in hinglish.

{chat_history}
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    messagee_place_holder = MessagesPlaceholder(variable_name="chat_history")
    return ChatPromptTemplate.from_messages([system_message_prompt,messagee_place_holder, human_message_prompt])



def main():

    st.header("Interviewer Chatbot (IC)🧠🤖")


    message_placeholder = st.container()
    message_placeholder.markdown('Bot 🤖:   ' + "Hi. . . I am IC.")
    message_placeholder.markdown('Bot 🤖:   ' + "Please give short introduction of yourself.")

    # Initialize Streamlit chat UI
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    def user(query):
        message_placeholder.markdown('Human 🧑:   ' + query)
    
    def bot(response):
        message_placeholder.markdown('Bot 🤖:   ' + response)

    




    with st.form('chat_input_form'):
        # Create two columns; adjust the ratio to your liking
        # col1, col2 = st.columns([7,1]) 

        # Use the first column for text input
        # with col1:
        query = st.text_input( "Ask your query:", placeholder= "Ask your query:", label_visibility='collapsed')
        # Use the second column for the submit button
        # with col2:
        submit = st.form_submit_button("Submit")


    if st.button("New Chat"):
        st.session_state.clear()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message["role"] == "human":
            message_placeholder.markdown('Human 🧑:   ' + message["content"])
        else :
            message_placeholder.markdown('Bot 🤖:   ' + message["content"])     

    if submit:

        st.session_state.messages.append({"role": "human", "content": query})
        llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        chat_prompt = get_chat_prompt()
        chain = ConversationChain(llm=llm, prompt=chat_prompt, memory = memory)
        
        for chat in st.session_state.chat_history:
            memory.save_context({"input": chat["input"]}, {"output": chat["output"]})
        # memory.save_context({"input": "hi"}, {"output": "whats up"})

        user(query)
    

        with get_openai_callback() as cb:
            #response = chain({"input_documents": docs, "human_input": query}, return_only_outputs=True)
            response = chain.run(query)
            print(cb)

        bot(response)

        st.session_state.messages.append({"role": "ai", "content": response})
        st.session_state.chat_history.append({"input": query, "output": response})
        # memory.save_context({"input": "hi"}, {"output": "whats up"})




with st.sidebar:
    st.title('🌐 Welcome to Interviewer Chatbot (IC)🧠🤖')
    st.markdown('''
                ### Hello there! 
                IC serves as a virtual interview assistant,
                offering users a practice platform to enhance 
                their interview skills within a chosen domain. 
                It is particularly valuable for individuals preparing 
                for job interviews, exams, or any scenario where effective 
                communication and domain knowledge are crucial.

                ''')
    st.markdown('''
            ### About
            This app is an LLM-powered chatbot built using:
            - [Streamlit](https://streamlit.io/)
            - [LangChain](https://python.langchain.com/)
            - [OpenAI](https://platform.openai.com/docs/models) LLM model
            ''')

    st.markdown('''
            ### Developed by [Nishant Singh Parihar](https://nishantparihar.github.io/)
            ''')
         

if __name__ == '__main__':
    main()
