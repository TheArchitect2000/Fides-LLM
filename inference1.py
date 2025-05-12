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

from langchain.vectorstores import Chroma, FAISS 
from langchain.embeddings import OpenAIEmbeddings

from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

from langchain.tools.retriever import create_retriever_tool

from dotenv import load_dotenv
import os

#######################
# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key1 = os.getenv("API_KEY1")

# Use the API key
print(f"Using API Key: {api_key1}")

#######################
# calling tools
arxivwrapper = ArxivAPIWrapper(top_k_result=1, doc_content_chars_max=200)
arxivtool = ArxivQueryRun(api_wrapper=arxivwrapper)

wikipediawrapper = WikipediaAPIWrapper(top_k_result=1, doc_content_chars_max=200)
wikipediatool = WikipediaQueryRun(api_wrapper=wikipediawrapper)

searchtool = DuckDuckGoSearchRun(name="DuckSearch1")

embedding1 = OpenAIEmbeddings(model="text-embedding-3-large", api_key=api_key1)
db = Chroma(persist_directory="chroma_langchain_db", embedding_function=embedding1, collection_name="example_collection")
db.get()
retriver1 = db.as_retriever()
retrivertool1 = create_retriever_tool(retriver1, "FidesInnovaInformationDatabase", "Search any information Fides Innova ZKP, zk-IoT, zkSensor, zkMultiSensor, Verifiable Agentic AI")

########################
# Initializing the agent


# db.similarity_search("what's zkmultisense?", k=1)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, api_key=api_key1)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in Fides Innova Blockchain technology. Based on the context, answer the question."),
    ("human", "Question = {question}"),
    ("human", "Context = {context}"),
])

chain = prompt | llm

def query(question):
    context = db.similarity_search(question, k=1)
    return chain.invoke({"question": question, "context": context[0].page_content}).content, context[0].metadata

st.title("Ask anything about Fides Innova project:")

user_input = st.text_input("Please type your question:")

if user_input:
    st.write("Answer:")
 #   st.success(user_input)
    
    answer, metadata = query(user_input)
    st.write(answer)

    st.subheader(metadata["type"])
    if metadata["type"]=="Web":
        st.write(metadata["source"])
    if metadata["type"]=="PDF":
        st.write(metadata["title"] + " | " + metadata["subject"])
    if metadata["type"]=="YouTube":
        st.write("https://www.youtube.com/watch?v="+metadata["source"])
        try:
            video_file = "https://www.youtube.com/watch?v="+metadata["source"]
    #        with open(video_file, 'rb') as f:
    #            video_bytes = f.read()
            st.video(video_file)
        except FileNotFoundError:
            st.error("File not found.")
