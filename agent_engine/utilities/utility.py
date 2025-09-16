from pydantic import BaseModel, Field, EmailStr
from agent_engine.utilities.document_loaders import pdfloader
from agent_engine.chat_model import model
from agent_engine.prompt import infoExtractorPrompt
from . import document_loaders


def infoextractor(resume_path: str):
    """Extract structured information from resume content using a language model."""
    resume_content = document_loaders.pdfloader(resume_path)

    class extracted_info(BaseModel):
        name: str = Field(default = None, description="full name of the candidate")
        age: int = Field(default = None, description="age of the candidate") 
        email: EmailStr = Field(default = None, description="email of the candidate")
        skills: str = Field(default = None, description="summary skills of the candidate")
        Certifications: str = Field(default = None, description="summary certifications of the candidate")
        experience: str = Field(default = None, description="summary professional experience of the candidate")
        achievements: str = Field(default = None, description="summary achievements of the candidate")
        domain_knowledge: str = Field(default = None, description="summary domain knowledge of the candidate")
        communication_skills: str = Field(default = None, description="summary communication skills of the candidate")
        education : str = Field(default = None, description="summary educational background of the candidate")
        softskills : str = Field(default = None, description="summary soft skills of the candidate")
        hobbies : str = Field(default = None, description="summary hobbies of the candidate")
        internships : str = Field(default = None, description="summary internships of the candidate")
        achievements : str = Field(default = None, description="summary achievements of the candidate")
        miscellaneous : str = Field(default = None, description="summary any other relevant information about the candidate")

    structured_model = model.with_structured_output(extracted_info)

    messages = [
        (
            "system",
            infoExtractorPrompt
        ),
        ("human", resume_content),
    ]

    response = structured_model.invoke(messages)
    return response

