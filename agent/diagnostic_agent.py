from agent.router import route_query

from agent.response_formatter import format_response

from agent.agent_core import agent

# ============================================================
# RUN WIN DIAG
# ============================================================

def run_diagnostic(query: str, thread_id: str):

    # ========================================================
    # 1. CLASSIFY QUERY
    # ========================================================

    route = route_query(query)


    # ========================================================
    # 2. RUN AGENT
    # ========================================================

    result = agent.invoke(

        {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        },

        context={
            "route": route.route
        },

        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )


    # ========================================================
    # 3. GET FINAL AGENT MESSAGE
    # ========================================================

    final_message = result["messages"][-1]


    # ========================================================
    # 4. STRUCTURE DIAGNOSTIC RESPONSES
    # ========================================================

    if route.route in ["DIAGNOSTIC", "BOTH"]:

        structured_response = format_response(

            question=query,

            information=final_message.content
        )


        return {
            "route": route.route,
            "structured_response": structured_response,
            "raw_response": final_message.content
        }


    # ========================================================
    # 5. KNOWLEDGE RESPONSE
    # ========================================================

    return {
        "route": route.route,
        "structured_response": None,
        "raw_response": final_message.content
    }


# ============================================================
# CLI CHAT
# ============================================================

def run_chat():

    print("\n================ WIN DIAG AI ================\n")

    print("Hi, this is WinDiag AI. It is ready for you.")
    print("Type 'exit' to stop.\n")


    # ========================================================
    # CONVERSATION ID
    # ========================================================

    thread_id = "winddiag-user-1"


    while True:

        query = input("\nYou: ").strip()


        # ====================================================
        # EXIT
        # ====================================================

        if query.lower() == "exit":

            print("\nWinDiag AI: Goodbye!")

            break


        # ====================================================
        # RUN WIN DIAG
        # ====================================================

        result = run_diagnostic(

            query=query,

            thread_id=thread_id
        )


        # ====================================================
        # ROUTE
        # ====================================================

        print(
            f"\n[Router] Route: {result['route']}"
        )


        # ====================================================
        # RESPONSE
        # ====================================================

        print("\nWinDiag AI:")


        # ====================================================
        # STRUCTURED DIAGNOSTIC RESPONSE
        # ====================================================

        if result["structured_response"]:

            structured_response = result["structured_response"]


            print("\nObserved:")

            for item in structured_response.observed:

                print("-", item)


            print("\nPossible Contributors:")

            for item in structured_response.possible_contributors:

                print("-", item)


            print("\nConfirmed Findings:")

            for item in structured_response.confirmed_findings:

                print("-", item)


            print("\nRecommendations:")

            for item in structured_response.recommendations:

                print("-", item)


        # ====================================================
        # KNOWLEDGE RESPONSE
        # ====================================================

        else:

            print(
                result["raw_response"]
            )


# ============================================================
# RUN ONLY WHEN THIS FILE IS EXECUTED DIRECTLY
# ============================================================

if __name__ == "__main__":

    run_chat()