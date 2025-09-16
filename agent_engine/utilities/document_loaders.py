from langchain_community.document_loaders import PyPDFLoader

def pdfloader(file_path: str) -> str:

    loader = PyPDFLoader(file_path)
    docs = loader.load()
    content = ""

    for x in docs:
        content += x.page_content + "\n"

    return content




