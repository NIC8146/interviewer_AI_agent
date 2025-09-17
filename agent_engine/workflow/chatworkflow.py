from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from agent_engine.chat_model import ChantModel
from typing import Literal, TypedDict, Annotated
from langgraph.graph.message import add_messages
from agent_engine.prompt import chatSystemPrompt
from langgraph.checkpoint.memory import InMemorySaver




class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    process_explainations: Annotated[list[BaseMessage], add_messages]
    processexplained : bool


def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = ChantModel.invoke(messages)

    # response store state
    return {'messages': [response]}


def explainer_node(state: ChatState):

    # take user query from state
    messages = state['process_explainations']

    # send to llm
    response = ChantModel.invoke(messages)

    # response store state
    return {'process_explainations': [response]}

def conditional_edge(state: ChatState) -> Literal["chat_node", "explainer_node"]:
    if state['processexplained']:
        return "chat_node"
    else:
        return "explainer_node"

checkpointer = InMemorySaver()
graph = StateGraph(ChatState)


graph.add_node('chat_node', chat_node)
graph.add_node('explainer_node', explainer_node)


graph.add_conditional_edges(START, conditional_edge)
graph.add_edge('chat_node', END)
graph.add_edge('explainer_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

initial_state = {
    'messages': [SystemMessage(content="what is capital of india?"),HumanMessage(content="tell me")],
    'process_explainations': [SystemMessage(content="who are you")],
    'processexplained': False
}
