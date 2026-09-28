from agent.agent_core import agent


def chat(question, thread_id):

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        context={
            "route": "DIAGNOSTIC"
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return result["messages"][-1].content


print("MESSAGE 1")
print(chat(
    "My name is Sundaram.",
    "test-thread"
))

print("\nMESSAGE 2")
print(chat(
    "What is my name?",
    "test2-thread"
))