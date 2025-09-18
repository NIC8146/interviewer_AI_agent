from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from agent_engine.chat_model import chatModel, evaluatorModel
from typing import Literal, TypedDict, Annotated
from langgraph.graph.message import add_messages
from agent_engine.prompt import chatSystemPrompt, evaluatorForExplainerPrompt, introSystemPrompt, BehaviourEvaluatorPrompt
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
    behaviourEvaluation: Annotated[list[BaseMessage], add_messages]
    BehaviourEvaluator: Literal["Continue", "endSuccessfully", "interrupt"]
    ReportGenerated: bool

def pseudo_start(state: ChatState):
    print("in pseudo start")
    return {'started': True}

def chat_node(state: ChatState):
    print("chat node")
    # take user query from state
    messages = state['messages']

    # send to llm
    response = chatModel.invoke(messages)

    # response store state
    return {'messages': [response]}

def explainer_node(state: ChatState):

    print("explainer node")

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

def behaviour_evaluation_node(state: ChatState):
    print("behaviour evaluation node")
    user_response = interrupt("useranswer")

    class EvaluatorState(BaseModel):
        BehaviourEvaluator: Literal["Continue", "endSuccessfully", "interrupt"]
        evaluationDescription: str
    
    if state["processexplained"]:
        state['messages'].append(HumanMessage(content=user_response))
        messages = state['messages'] + [SystemMessage(content=BehaviourEvaluatorPrompt)]
    else:
        state['process_explainations'].append(HumanMessage(content=user_response))
        messages = state['process_explainations'] + [SystemMessage(content=BehaviourEvaluatorPrompt)]

    structured_model = evaluatorModel.with_structured_output(EvaluatorState)

    response = structured_model.invoke(messages)

    description = response.evaluationDescription

    return {'behaviourEvaluation': [AIMessage(content=description)], 'evaluatorProgress': response.evaluatorProgress}

def reportGeneratorNode(state: ChatState):
    print("report generator node")
    return {'ReportGenerated': True}

def conditionalEdgeforStart(state: ChatState) -> Literal["chat_node", "explainer_node"]:
    if state['processexplained']:
        return "chat_node"
    else:
        return "explainer_node"
  
def evaluatorForExplainer(state: ChatState) -> Literal["chat_node", "behaviour_evaluation_node"]:
    if state['processexplained']:
        return "chat_node"
    else:
        return "behaviour_evaluation_node"

def conditionalEdgeForBehaviourEvaluator(state: ChatState) -> Literal["pseudo_start", "reportGeneratorNode", END]:
    if state['evaluatorProgress'] == "Continue":
        return "pseudo_start"
    elif state['evaluatorProgress'] == "endSuccessfully":
        return "reportGeneratorNode"
    else:
        return END

conn = sqlite3.connect(database=os.path.join(settings.BASE_DIR, 'db.sqlite3'), check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)


graph.add_node('pseudo_start', pseudo_start)
graph.add_node('chat_node', chat_node)
graph.add_node('explainer_node', explainer_node)
graph.add_node('reportGeneratorNode', reportGeneratorNode)
graph.add_node('behaviour_evaluation_node', behaviour_evaluation_node)


graph.add_edge(START, "pseudo_start")
graph.add_conditional_edges("pseudo_start", conditionalEdgeforStart)
graph.add_conditional_edges('explainer_node', evaluatorForExplainer)
graph.add_edge('chat_node', "behaviour_evaluation_node")
graph.add_conditional_edges('behaviour_evaluation_node', conditionalEdgeForBehaviourEvaluator)
graph.add_edge('reportGeneratorNode', END)
# graph.add_edge('behaviour_evaluation_node', END)


chatbot = graph.compile(checkpointer=checkpointer)

initial_state = {
    'messages': [SystemMessage(content=chatSystemPrompt)],
    'process_explainations': [SystemMessage(content=introSystemPrompt)],
    'processexplained': False,
    'started': False,
    'resume_uploaded' : False
}
