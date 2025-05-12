
############################ Using the retriever in an LLM 
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

retriever1 = mydb1.as_retriever(search_kwargs={"k":1})

ChatPromptTemplate2 = ChatPromptTemplate.from_messages(
    [
        ('system','As a Blockchain Expert respond to the queries. The Goal is to provide detailed-oriented answers. The Style is technical discussion. The context is {context}.'),
        ('human', '{input}'),
    ])

firstChain = create_stuff_documents_chain(ChatOpenAIModel1,ChatPromptTemplate2)
chain2 = create_retrieval_chain(retriever1, firstChain)

result2 = chain2.invoke({"input":query1})
print(result2["answer"])


############################## Step 2: Set up Contract ===
contract_address = Web3.to_checksum_address("0x1234567890abcdef1234567890abcdef12345678")  # Replace with your contract address
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

############################## Step 3: Query Sensor Data from Blockchain ===
sensor_id = 1
location, value, timestamp = contract.functions.getSensorData(sensor_id).call()
onchain_data = f"Sensor ID: {sensor_id}, Location: {location}, Value: {value}, Timestamp: {timestamp}"

print("📡 On-chain sensor data retrieved:")
print(onchain_data)

