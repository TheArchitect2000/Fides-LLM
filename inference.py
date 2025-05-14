## Creating Fides Innova agent
# 1- Wrapper for different data sources such as Arxiv, WikiPedia, DuckDuckGo, 
# 2- Adding RAG as a tool
# 3- Connector to Databases
# 4- LLM Fine-tunning
# 5- Connector to Blockchain RPC

# 6- Multi-agent structure (Sequential agent, Hirechacy agent, Nested agent) for Verifiable Agentic AI
# 6-1- Program Commitment Generator Agent: Read the user program (e.g., TeslaV17.cpp) and generate a commitment file (e.g., Tesla17Commitment.json).
# 6-2- Commitment Uploader Agent: Read the commitment file (e.g., Tesla17Commitment.json) and upload it on the Fides Innova blockchain (e.g., rpc.fidesinnova.io).
# 6-3- Device Registration Agent: Register the device on an IoT server (e.g., zkSensor.tech IoT server) and assign a commitment file (e.g., Tesla17Commitment.json) on the Fides Innova blockchain to the registered device. 
# 6.4- Device Proof Generation: This steps should be dne by the device or user program itself. Therefore, Fides Innova cannot make it agentic-based. We have provided a .h library to add proof generation capabilities to the user's program. User sends its proof to the blockchain.
# 6.5- Proof Verification Agent: Receive the verification request from a user and search the blockchain, verify it and send the result back to the user. Also, provides a link for the user via explorer.fidesinnova.io
# 6.6- Device Driving Agent: Train the user for proper device usage.

# pip install python-dotenv
# pip install streamlit

import streamlit as st
from dotenv import load_dotenv
import json 
import os

from langchain.vectorstores import Chroma, FAISS 
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper, GoogleSerperAPIWrapper
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, create_openai_tools_agent, AgentType, AgentExecutor
from langchain.agents.output_parsers.json import JSONAgentOutputParser
from langchain_core.output_parsers.json import JsonOutputParser

from langchain.tools.retriever import create_retriever_tool
from langchain.callbacks import StreamlitCallbackHandler

## needed for chat history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

#######################
# Load environment variables from .env file
load_dotenv()

# Get the API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

#######################
# calling tools
arxivwrapper = ArxivAPIWrapper(top_k_result=1, doc_content_chars_max=200)
arxivtool = ArxivQueryRun(api_wrapper=arxivwrapper)

wikipediawrapper = WikipediaAPIWrapper(top_k_result=1, doc_content_chars_max=200)
wikipediatool = WikipediaQueryRun(api_wrapper=wikipediawrapper)

# searchtool = DuckDuckGoSearchRun(name="DuckSearch1")
searchWrapper = GoogleSerperAPIWrapper()
searchtool = Tool(
        name = "Search",
        func = searchWrapper.run,
        description = "useful for when you need to answer questions about current events. You should ask targeted questions",
    )

def alaki(x):
    return "alaki.com"

alakitool = Tool(
        name = "Alaki",
        func = alaki,
        description = "When you need to answer questions about Alaki. You should ask targeted questions",
    ) 

embedding1 = OpenAIEmbeddings(model="text-embedding-3-large")
db = Chroma(persist_directory="chroma_langchain_db", embedding_function=embedding1, collection_name="example_collection")
db.get()
retriver1 = db.as_retriever()
# retrivertool1 = create_retriever_tool(retriver1, "FidesInnovaInformationDatabase", "Search any information Fides Innova ZKP, zk-IoT, zkSensor, zkMultiSensor, Verifiable Agentic AI")

#######################                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
# chain = prompt | llm
def query(question):
    context = db.similarity_search(question, k=1)
    # return chain.invoke({"question": question, "context": context[0].page_content}).content, context[0].metadata
    return {"context":context[0].page_content, "metadata":context[0].metadata}

retrivertool1 = Tool(
        name = "FidesInnovaInfoDB",
        func = query,
        description = "Search any information Fides Innova ZKP, zk-IoT, zkSensor, zkMultiSensor, Verifiable Agentic AI",
    ) 

########################
llm = ChatOpenAI(model="gpt-4o-mini")

########################
# Session management
def get_session_history(session:str)->BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id]=ChatMessageHistory()
    return st.session_state.store[session_id]

########################
# Initialize the agent

tool_list = [alakitool, retrivertool1, searchtool, wikipediatool, arxivtool]

prompt = ChatPromptTemplate.from_messages([
   ("system", "You are an expert in Fides Innova Verifiable Computing technology. Based on the context, answer the question, and return the output in a json format without mentioning the json word. If you found something in the FidesInnovaInfoDB database, then return two keywords in the json content as (answer, metadata). When sending the metadata, keep the key and the value of both the type and the source. Otherwise, only return the (answer)."),
   ("human", "Question = {input}"),
   MessagePlaceholder("chat_history"),
   MessagesPlaceholder("agent_scratchpad")
])

fidesagent = create_openai_tools_agent(llm, tool_list, prompt)
fidesagentexecutor = AgentExecutor(agent=fidesagent, tools=tool_list)
fidesagentexecutorwithhistory = RunnableWithMessageHistory(fidesagentexecutor, get_session_history, output_messages_key="Assitant_Response", input_messages_key="input", history_messages_key="chat_history")

fidesagentexecutor2 = fidesagentexecutor | JsonOutputParser()

#######################
# db.similarity_search("what's zkmultisense?", k=1)

#######################
st.title("Fides Innova AI Agent")
# user_input = st.text_input("Please type your question:")

if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant","content":"Ask me anything about Fides Innova verifiable computing technology and project."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

if prompt:=st.chat_input(placeholder="- What's zk-IoT?\n- How to install a new IoT Server and connect to the Fides network?\n- How to install a zkDevice?\n- How to add Fides library to my C++ code?\n- How to generate and submit a program commitment?\n- How to generate a zero-knowledge proof (ZKP)?"):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler( st.container(), expand_new_thoughts=False)

        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]

        response = fidesagentexecutor.invoke({"input":prompt}, cfg)
        myjsonoutputparser = JsonOutputParser()
        jsonresponse = json.loads(response["output"])

        st.session_state.messages.append({'role':'assistant',"content":response})

        st.write(jsonresponse["answer"])

        if "metadata" in jsonresponse:
            if jsonresponse["metadata"]: 
                metadata = jsonresponse["metadata"]
                st.subheader(metadata["type"])
                if metadata["type"]=="Web":
                    st.write(metadata["source"])
                if metadata["type"]=="PDF":
                    st.write(metadata["title"] + " | " + metadata["subject"])
                if metadata["type"]=="YouTube":
                    st.write("https://www.youtube.com/watch?v="+metadata["source"])
                    try:
                        video_file = "https://www.youtube.com/watch?v="+metadata["source"]
                        st.video(video_file)
                    except FileNotFoundError:
                        st.error("File not found.")
 