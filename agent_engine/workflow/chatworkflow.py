from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from agent_engine.chat_model import chatModel, evaluatorModel
from typing import Literal, TypedDict, Annotated
from langgraph.graph.message import add_messages
from agent_engine.prompt import chatSystemPrompt, evaluatorForExplainerPrompt, introSystemPrompt
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from interviewer_agent import settings
import os
from pydantic import BaseModel, Field




class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    process_explainations: Annotated[list[BaseMessage], add_messages]
    processexplained : bool
    started : bool
    evaluatorProgress : Literal["ProceedNext", "Continue", "Messing Around"]


def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = chatModel.invoke(messages)

    # response store state
    return {'messages': [response]}


def explainer_node(state: ChatState):


    class ProcessExplainedState(BaseModel):
        processexplained: bool  = Field(description="Whether the process has been explained and user agrees to proceed")
        message: str = Field(description="The response message from the AI")

    # take user query from state
    messages = state['process_explainations']

    structured_model = chatModel.with_structured_output(ProcessExplainedState)
    # send to llm
    response = structured_model.invoke(messages)

    response_message = response.message
    if response.processexplained:
        return {'started': True, 'process_explainations': [response_message], 'processexplained': True}
    else:

        # response store state
        return {'started': True, 'process_explainations': [response_message]}

def conditionalEdgeforStart(state: ChatState) -> Literal["chat_node", "explainer_node"]:
    if state['processexplained']:
        return "chat_node"
    else:
        return "explainer_node"

def conditionalEdgeForEvaluator(state: ChatState) -> Literal["chat_node", "explainer_node", END]:
    if state['evaluatorProgress'] == "ProceedNext":        
        return "chat_node"
    elif state['evaluatorProgress'] == "Continue":
        return "explainer_node"
    else:
        return END
    

def evaluatorForExplainer(state: ChatState):

    class EvaluatorState(TypedDict):
        evaluatorProgress : Literal["ProceedNext", "Continue", "Messing Around"]

    structuredModel = evaluatorModel.with_structured_output(EvaluatorState)

    evaluator_state = structuredModel.invoke(state["process_explainations"] + [SystemMessage(content=evaluatorForExplainerPrompt)])


    return {'evaluatorProgress': evaluator_state["evaluatorProgress"]}

conn = sqlite3.connect(database=os.path.join(settings.BASE_DIR, 'db.sqlite3'), check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
# checkpointer = InMemorySaver()
graph = StateGraph(ChatState)


graph.add_node('chat_node', chat_node)
graph.add_node('explainer_node', explainer_node)
graph.add_node('evaluatorForExplainer', evaluatorForExplainer)


graph.add_conditional_edges(START, conditionalEdgeforStart)
graph.add_conditional_edges('evaluatorForExplainer', conditionalEdgeForEvaluator)
# graph.add_edge('explainer_node', 'evaluatorForExplainer')
graph.add_edge('explainer_node', END)
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

initial_state = {
    'messages': [SystemMessage(content=chatSystemPrompt)],
    'process_explainations': [SystemMessage(content=introSystemPrompt)],
    'processexplained': False,
    'started': False 
}
