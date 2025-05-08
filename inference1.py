import streamlit as st

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

#######################
# pip install python-dotenv
# pip install streamlit
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key1 = os.getenv("API_KEY1")

# Use the API key
print(f"Using API Key: {api_key1}")
#######################

embedding1 = OpenAIEmbeddings(model="text-embedding-3-large", api_key=api_key1)
db = Chroma(persist_directory="chroma_langchain_db", embedding_function=embedding1, collection_name="example_collection")
db.get()

# db.similarity_search("what's zkmultisense?", k=1)

from langchain_openai import ChatOpenAI
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, api_key=api_key1)

from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Based on the context, answer the question."),
    ("human", "Question = {question}"),
    ("human", "Conext = {context}"),
])

chain = prompt | llm

def query(question):
    context = db.similarity_search(question, k=1)
    return chain.invoke({"question": question, "context": context[0].page_content}).content, context[0].metadata

st.title("Ask anything about Fides Innova project:")

user_input = st.text_input("Your input")

if user_input:
    st.write("Your output")
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
