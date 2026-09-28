from langchain_core.runnables import RunnableLambda

def make_upper(text):
    print("Inside make_upper:")
    print("Value:", text)
    print("Type:", type(text))

    return text.upper()


def add_message(text):
    print("\nInside add_message:")
    print("Value:", text)
    print("Type:", type(text))

    return text + "!!!"


chain = (
    RunnableLambda(make_upper)
    | RunnableLambda(add_message)
)

result = chain.invoke("hello windiag")

print("\nFinal result:")
print(result)
print(type(result))