from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model="gpt-4o-mini"
)

ChantModel = ChatOpenAI(
    model="gpt-4o-mini"
)
