from langchain_core.tools import tool


@tool
def request_user_approval(action: str) -> str:
    """
    Ask the user for explicit approval before performing
    an action that could modify the Windows computer.

    This tool does not perform the action.
    It only requests approval.
    """

    print("\n" + "=" * 60)
    print("USER APPROVAL REQUIRED")
    print("=" * 60)

    print(f"\nProposed action:")
    print(action)

    answer = input("\nDo you approve this action? (yes/no): ").strip().lower()

    if answer in ["yes", "y"]:

        return "USER_APPROVED"

    return "USER_DENIED"
# ============================================================
# TEST APPROVAL TOOL
# ============================================================

if __name__ == "__main__":

    result = request_user_approval.invoke({
        "action": "Clear temporary files from the Windows computer"
    })

    print("\nApproval result:")
    print(result)