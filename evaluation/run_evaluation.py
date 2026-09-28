import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.test_cases import test_cases
from agent.router import route_query
from agent.agent_core import agent


def get_called_tools(messages):
    """
    Extract the names of tools called by the agent.
    """

    tools_called = []

    for message in messages:

        if hasattr(message, "tool_calls") and message.tool_calls:

            for tool_call in message.tool_calls:

                tool_name = tool_call.get("name")

                if tool_name:
                    tools_called.append(tool_name)

    return tools_called


print()
print("=" * 70)
print("WIN DIAG AI - EVALUATION")
print("=" * 70)


route_passed = 0
route_failed = 0
agent_passed = 0
agent_failed = 0


for index, test_case in enumerate(test_cases, start=1):

    question = test_case["question"]
    expected_route = test_case["expected_route"]

    print()
    print("=" * 70)
    print(f"TEST CASE {index}")
    print("=" * 70)

    print()
    print("Question:")
    print(question)

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    try:

        route = route_query(question)

        actual_route = route.route

        route_result = (
            "PASS"
            if actual_route == expected_route
            else "FAIL"
        )

        if route_result == "PASS":
            route_passed += 1
        else:
            route_failed += 1

        print()
        print("Expected Route:")
        print(expected_route)

        print()
        print("Actual Route:")
        print(actual_route)

        print()
        print("Route Result:")
        print(route_result)

    except Exception as error:

        route_failed += 1

        print()
        print("Router ERROR:")
        print(error)

        continue

    # --------------------------------------------------------
    # AGENT
    # --------------------------------------------------------

    try:

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
                "route": actual_route
            },
            config={
                "configurable": {
                    "thread_id": f"evaluation-{index}"
                }
            }
        )

        agent_passed += 1

        messages = result["messages"]

        tools_called = get_called_tools(messages)

        print()
        print("Agent Result:")
        print("PASS")

        print()
        print("Tools Called:")

        if tools_called:
            for tool in tools_called:
                print(f"- {tool}")
        else:
            print("- None")

        print()
        print("Final Response:")

        print(messages[-1].content)

    except Exception as error:

        agent_failed += 1

        print()
        print("Agent Result:")
        print("ERROR")

        print()
        print(error)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("EVALUATION SUMMARY")
print("=" * 70)

print()
print(f"Total Tests: {len(test_cases)}")

print()
print(
    f"Route Passed: {route_passed}/{len(test_cases)}"
)

print(
    f"Route Failed: {route_failed}/{len(test_cases)}"
)

print()
print(
    f"Agent Completed: {agent_passed}/{len(test_cases)}"
)

print(
    f"Agent Failed: {agent_failed}/{len(test_cases)}"
)

print()
print("=" * 70)
print("EVALUATION COMPLETE")
print("=" * 70)