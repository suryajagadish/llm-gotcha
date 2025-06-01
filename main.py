# load the dotenv file to get access to required evn variable
from dotenv import load_dotenv
load_dotenv(override=True)

# custom system prompt to set the characteristics of the LLM and it's response
from prompt import custom_system_prompt

from langgraph.graph import START, MessagesState, StateGraph
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_template = ChatPromptTemplate.from_messages([SystemMessage(custom_system_prompt), MessagesPlaceholder(variable_name="messages")])
model = init_chat_model("gpt-4o-mini", model_provider="openai")
workflow = StateGraph(state_schema=MessagesState)

def call_model(state: MessagesState):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": response}

workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
config = {"configurable": {"thread_id": "00001"}}
app = workflow.compile(checkpointer=memory)

while True:
    query = input("\nuser >> ")
    input_messages = [HumanMessage(query)]
    output = app.invoke({"messages": input_messages}, config)
    response = output["messages"][-1]

    print(f"\nassistant >> {response.content}")