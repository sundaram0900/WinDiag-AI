# from langchain_huggingface import (
#     HuggingFaceEndpoint,
#     ChatHuggingFace
# )
#
# from langchain.agents import create_agent
#
# from dotenv import load_dotenv
#
# load_dotenv()
#
#
# llm = HuggingFaceEndpoint(
#     repo_id="Qwen/Qwen3-4B-Instruct-2507",
#     task="text-generation",
#     max_new_tokens=256,
#     temperature=0.2
# )
#
# chat_model = ChatHuggingFace(
#     llm=llm
# )
#
#
# agent = create_agent(
#     model=chat_model,
#     tools=[],
#     system_prompt="""
# You are a helpful assistant.
#
# Remember information from earlier messages in the
# current conversation and use it when answering
# follow-up questions.
# """
# )
#
#
# messages = [
#     {
#         "role": "user",
#         "content": "My laptop has 16 GB of RAM."
#     }
# ]
#
#
# result = agent.invoke({
#     "messages": messages
# })
#
#
# print("\n================ RESPONSE 1 ================\n")
#
# for message in result["messages"]:
#     print(
#         type(message).__name__,
#         ":",
#         message.content
#     )
#
# # ============================================================
# # SECOND QUESTION
# # ============================================================
#
# messages = result["messages"]
#
# messages.append({
#     "role": "user",
#     "content": "What about the CPU?"
# })
#
# result = agent.invoke({
#     "messages": messages
# })
#
# print("\n================ RESPONSE 2 ================\n")
#
# for message in result["messages"]:
#     print(
#         type(message).__name__,
#         ":",
#         message.content
#     )



from langchain_huggingface import (
    HuggingFaceEndpoint,
    ChatHuggingFace
)

from langchain.agents import create_agent

from dotenv import load_dotenv

load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-4B-Instruct-2507",
    task="text-generation",
    max_new_tokens=256,
    temperature=0.2
)

chat_model = ChatHuggingFace(
    llm=llm
)


agent = create_agent(
    model=chat_model,
    tools=[],
    system_prompt="""
You are a helpful assistant.
"""
)


result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "My laptop has 16 GB of RAM."
        }
    ]
})


print("\n================ RESULT ================\n")

print("Result type:")
print(type(result))

print("\nResult:")
print(result)

print("\nResult keys:")
print(result.keys())

print("\nMessages:")
for message in result["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content
    )