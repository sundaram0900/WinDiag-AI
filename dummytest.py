import langchain
import langchain_core

print("LangChain:", langchain.__version__)
print("LangChain Core:", langchain_core.__version__)

from langchain.agents import create_agent

print("create_agent imported successfully!")