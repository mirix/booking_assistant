from date_search import check_availability
from book_appointment import appointment_booking

import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
from langchain.tools.render import render_text_description
#from langchain_core.output_parsers import JsonOutputParser

# Set up the LLM which will power our application.
# Athene-V2-Agent (a function-calling fine-tune of Qwen-2.5-72B-Intruct) works better
# but even the 4bit quantisation does not fit on my RTX 3090
# Qwen2.5-Coder-32B-Instruct works reasonably well
# whereas smaller models struggle if prompts are not very precise

#model = ChatOllama(model='hf.co/bartowski/Athene-V2-Agent-GGUF:Q4_K_M', temperature=0)
model = ChatOllama(model='hf.co/bartowski/Qwen2.5-Coder-32B-Instruct-GGUF:Q4_K_M', temperature=0)
#model = ChatOllama(model='hf.co/bartowski/QwQ-32B-Preview-GGUF:Q4_K_M', temperature=0)

# Define tools available.
@tool('check_availabe_slots')
def check_availabe_slots(input: str) -> dict:
    'Check if the the date suggested by the user is available.'
    return check_availability(input)

@tool('book_apointment', return_direct=True)
def book_apointment(input: str) -> dict:
    'Book an appointment on the selected slot.'
    return appointment_booking(input)

@tool
def converse(input: str) -> str:
    'Provide a natural language response using the user input.'
    return model.invoke(input)


tools = [check_availabe_slots, book_apointment, converse]

model = model.bind_tools(tools)

# Configure the system prompts
rendered_tools = render_text_description(tools)

system_prompt = '''

BACKGROUND

- You are an appointment booking assistant.

- You assist the user in finding available slots and booking appointments.


POLICIES

You strictly obey the following rules:

- Politely refuse to book any slot that is longer than 1 hour. Inform the users that they can only book one-hour slots instead.

- Politely refuse to anwser any questions not related to appointment scheduling.

- Do not make up any information.


TOOLS

- Use the provided tools as required.

- Use the check_availabe_slots tool to search the calendar when so requested or if a specific date and time is not provided.

- The check_availabe_slots tool provides a dictionary with a "response" and a "availability_list". Always quote the tool response verbatim followed by each of the items from the availability_list as markdown bullet points.

- Use the book_apointment tool to book the appointment if a specific date and time is provided and so requested.

- The book_apointment tool provides a string as a response. Always quote the tool response verbatim.


CONVERSATION HISTORY

Here is the conversation history: {context}.


'''

# Here is the conversation history: {context}.

prompt = ChatPromptTemplate.from_messages(
    [('system', system_prompt), ('user', '{input}'), ('placeholder', '{agent_scratchpad}')]
)

# Define a function which returns the chosen tools as a runnable, based on user input.
def tool_chain(model_output):
    tool_map = {tool.name: tool for tool in tools}
    chosen_tool = tool_map[model_output['name']]
    return itemgetter('arguments') | chosen_tool

# The main chain: an LLM with tools.
#chain = prompt | model | JsonOutputParser() | tool_chain

agent = create_tool_calling_agent(model, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Set up message history.
msgs = StreamlitChatMessageHistory(key='langchain_messages')
if len(msgs.messages) == 0:
    msgs.add_ai_message('Hi! If you wish to book an appointment, please, indicate the desired date and time.')

# Set the page title.
st.title('Appointment Booking Assistant')

# Render the chat history.
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# React to user input
if input := st.chat_input('What is up?'):

    # Display user input and save to message history.
    st.chat_message('user').write(input)
    msgs.add_user_message(input)

    # Invoke chain to get reponse.
    response = agent_executor.invoke({'context': msgs, 'input': input})

    # Display AI assistant response and save to message history.
    st.chat_message('assistant').write(str(response['output']))
    msgs.add_ai_message(str(response['output']))
