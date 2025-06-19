### Creating Fides Innova agent
import streamlit as st
import json 
import os
import re
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

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
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from search_faiss import search

################################################
# Step 1:  calling tools
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

####### Create a retriever tool for Fides Innova information database
def query(question):
    context = search(question, k=1)
    # page_contents = list(map(lambda x:x.page_content, context))
    # meta_data = list(map(lambda x:x.metadata, context))
    # return {"context":page_contents, "metadata":meta_data}
    return {"context":context[0].page_content, "metadata":context[0].metadata}
    # return (context)

retrivertool1 = Tool(
        name = "FidesInnovaInfoDB",
        func = query,
        description = "Search any information about Fides Innova project and technology.",
    ) 

tool_list = [retrivertool1, searchtool, wikipediatool, arxivtool]

############################
# Step 2: Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# we are defining an agent, not a chain
# chain = prompt | llm

##############################################
# Step 3:Initialize the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """
     You are an expert in Fides Innova Verifiable Computing ZKP project. 
     Always respond strictly in valid JSON format like this: {{\"answer\": \"...\", \"metadata\": {{\"type\": \"...\", \"source\": \"...\", \"title\": \"...\"}}}}. Do not include markdown, backticks, or explanations outside the JSON. 
     Based on the context, answer the question, and return the output. 
     """),
# If you found something valuable in FidesInnovaInfoDB, the answer would be a list of documents that have page_content and metadata, these two should be used to create the answer and metadata.
#    ("system", "You are an expert in Fides Innova Verifiable Computing. Always respond strictly in valid JSON format like this: {\"answer\": \"...\", \"metadata\": {\"type\": \"...\", \"source\": \"...\"}}. Do not include markdown, backticks, or explanations outside the JSON."),
 #  ("system", "You are an expert in Fides Innova Verifiable Computing technology. "),
  #  ("system", "You are an expert in Fides Innova Verifiable Computing. Always return responses strictly in this JSON format: {\"answer\": \"...\", \"metadata\": {\"type\": \"...\", \"source\": \"...\"}}. Do not include any markdown, code formatting, or extra text before or after the JSON."),
   ("human", "Question = {input}"),
   MessagesPlaceholder("chat_history"),
   MessagesPlaceholder("agent_scratchpad")
])

############################################################
# Initialize the agent
fidesagent = create_openai_tools_agent(llm, tool_list, prompt)
fidesagentexecutor = AgentExecutor(agent=fidesagent, tools=tool_list)

# Session management
def get_session_history(session_id:str)->BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id]=ChatMessageHistory()
    return st.session_state.store[session_id]

# fidesagentexecutor2 = fidesagentexecutor | JsonOutputParser()

fidesagentexecutorwithhistory = RunnableWithMessageHistory(fidesagentexecutor, get_session_history, output_messages_key="output", input_messages_key="input", history_messages_key="chat_history")

############################
def get_or_create_session_id():
    import uuid
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

st.title("Fides Innova AI Assistant")
# user_input = st.text_input("Please type your question:")
# session_id=st.text_input("Session ID",value="default_session")
session_id = str(get_or_create_session_id())

import datetime
print("Fides-LLM started at", datetime.datetime.now())

if 'store' not in st.session_state:
    st.session_state.store={}

if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant",
         "content":"""
            Hi! How can I assist you today?"""}
    ]

if "messages2" not in st.session_state:
    st.session_state["messages2"]=[
        {"role":"assistant","content":"Ask me anything about Fides Innova’s verifiable computing technology.\n"}
    ]

for msg in st.session_state.messages2:
    st.chat_message(msg["role"]).write(msg["content"])


    # if msg["role"] == "assistant":
    #     try: 
    #         content = json.loads(msg["content"])
    #         output = json.loads(content["output"])
    #         answer = output["answer"]
    #         st.chat_message(msg["role"]).write(answer)
    #     except:
    #         st.chat_message(msg["role"]).write(msg["content"])
    # else:
    #     st.chat_message(msg["role"]).write(msg['content']['output']["answer"])

# for msg in st.session_state.messages:
#     if isinstance(msg['content'],dict):
#         if isinstance(msg['content']["output"],dict):
#             if "answer" in msg['content']['output'].keys():
#                 st.chat_message(msg["role"]).write(msg['content']['output']["answer"])      
#             else:
#                 st.chat_message(msg["role"]).write(msg['content']['output'])  
#         else:
#                 st.chat_message(msg["role"]).write(msg['content'])
#     else:
#         try:
#             content = json.loads(msg["content"])
#             output = json.loads(content["output"])
#             answer = output["answer"]
#             st.chat_message(msg["role"]).write(answer)
#         except:
#             st.chat_message(msg["role"]).write(msg['content'])

# Inject custom CSS to style the sidebar

st.markdown(
    """
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1f4e79 !important;  /* Professional sidebar blue */
        width: 300px !important;
    }

    [data-testid="stSidebarContent"] {
        width: 300px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }

    /* Optional: spacing adjustments */
    .css-1d391kg { padding: 1rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar content: centered logo, title, and external links
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://panel.zksensor.tech/img/logo/logo-dark-full.png" width="250">
            <div style="font-size: 28px; font-weight: bold; margin-top: 14px; color: white;">
                Fides Innova<br>AI Assistant
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---", unsafe_allow_html=True)

 #   st.markdown("### 🔗 Links", unsafe_allow_html=True)
    st.markdown("""
                <div style="color:white">
                <ul>
                    <li><a href="https://www.fidesinnova.io" target="_blank" style="color:white;">Website</a></li>
                    <li><a href="https://x.com/fidesinnova" target="_blank" style="color:white;">X</a></li>
                    <li><a href="https://www.youtube.com/@fidesinnova" target="_blank" style="color:white;">YouTube</a></li>
                    <li><a href="https://github.com/TheArchitect2000/iot-server" target="_blank" style="color:white;">IoT Server GitHub</a></li>
                    <li><a href="https://github.com/TheArchitect2000/zkiot-arm-siemens-iot2050-c" target="_blank" style="color:white;">ZKP Device Integration</a></li>
                    <li><a href="https://github.com/TheArchitect2000/Fides-Innova-WiKi?tab=readme-ov-file#fidesinnova-wiki" target="_blank" style="color:white;">Wiki</a></li>
                    <li><a href="http://agent1.fidesinnova.io:8502" target="_blank" style="color:white;">ZKP Integration Agent</a></li>
                </ul>
                </div>""",
                unsafe_allow_html=True
                )
    
if prompt := st.chat_input(placeholder="- How to install a new IoT Server and connect to the Fides network?\n- What's zk-IoT?\n- How to install a zkDevice?\n- How to add Fides library to my C++ code?\n- How to generate and submit a program commitment?\n- How to generate a zero-knowledge proof (ZKP)?"):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.messages2.append({"role":"user","content":prompt})

    # what user types will be written with a user icon, only to display
    st.chat_message("user").write(prompt)
    
    # what we types will be written with an assistant icon, only to display
    # all the call backs and chain-of-thoughts will be shown in side this container
    with st.chat_message("assistant"):
        
        # Streamlit gets the call_back responses
        st_cb = StreamlitCallbackHandler( st.container(), expand_new_thoughts=False)

        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        # for chat history
        cfg["configurable"] = {"session_id":session_id}
        current_session_history = get_session_history(session_id)
        current_session_history.add_user_message(prompt)

    #     response = fidesagentexecutorwithhistory.invoke({"input":prompt}, cfg)
        
    #     myjsonoutputparser = JsonOutputParser()
        
    #     import re

    #     raw_output = response["output"]
    #     clean_output = re.sub(r"```json|```", "", raw_output).strip()

    #     try:
    #         jsonresponse = json.loads(clean_output)
    #     except json.JSONDecodeError as e:
    #         st.error("⚠️ Failed to parse model output as JSON.")
    #         st.text(clean_output)
    #         raise e

    #    #  jsonresponse = json.loads(response["output"])

    #     parsed_response = fidesagentexecutor2.invoke({"input": prompt}, cfg)
    #     jsonresponse = parsed_response  # Already parsed dict

    #     current_session_history.add_ai_message(response["output"])

    #   parsed_response = fidesagentexecutor2.invoke({"input": prompt}, cfg)

        parsed_response = fidesagentexecutorwithhistory.invoke({
            "input": prompt
        }, cfg)


        # print("History = ", current_session_history.messages)
        # print("session id: " , session_id)
        # print("Get History: " , get_session_history(session_id))
        # # print(parsed_response)
        raw_output = parsed_response["output"]
        # print(raw_output)
    
        clean_output = re.sub(r"```json|```", "", raw_output).strip()

        try:
            jsonresponse = json.loads(clean_output)
        except json.JSONDecodeError as e:
            st.error("⚠️ Failed to parse model output as JSON.")
            st.text(raw_output)
            raise e

        # jsonresponse = parsed_response  # Already parsed dict

#        current_session_history.add_ai_message(json.dumps(jsonresponse))
        current_session_history.add_ai_message(raw_output)

        st.session_state.messages.append({'role':'assistant',"content":parsed_response})
        st.session_state.messages2.append({'role':'assistant',"content":jsonresponse["answer"]})

        st.write(jsonresponse["answer"])

        if "metadata" in jsonresponse:
            if jsonresponse["metadata"]: 
                metadata = jsonresponse["metadata"]
                st.subheader(metadata["type"])
                if metadata["type"]=="Web":
                    st.write(metadata["source"])
                if metadata["type"]=="GitHub":
                    st.write(metadata["source"])
                    try:
                        st.write(metadata["title"])
                    except:
                        pass
                if metadata["type"]=="PDF":
                    try:
                       st.write(metadata["title"] + " | " + metadata["subject"])
                    except:
                       st.write(metadata["title"])
                if metadata["type"]=="PPTX":
                    try:
                       st.write(metadata["source"])
                    except:
                        pass
                if metadata["type"]=="YouTube":
                    st.write("https://www.youtube.com/watch?v="+metadata["source"])
                    try:
                        video_file = "https://www.youtube.com/watch?v="+metadata["source"]
                        st.video(video_file)
                    except FileNotFoundError:
                        st.error("File not found.")
 