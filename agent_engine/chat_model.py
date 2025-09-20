from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


model = ChatOpenAI(
    model="gpt-4o-mini"
)

evaluatorModel = ChatOpenAI(
    model="gpt-4o-mini"
)

chatModel = ChatOpenAI(
    model="gpt-4o-mini"
)
