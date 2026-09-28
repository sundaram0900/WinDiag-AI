from pydantic import BaseModel


class DiagnosticResponse(BaseModel):

    observed: list[str]

    possible_contributors: list[str]

    confirmed_findings: list[str]

    recommendations: list[str]

if __name__ == "__main__":

    response = DiagnosticResponse(
        observed=[
            "RAM usage is 79.2%",
            "C: drive usage is 84.7%"
        ],

        possible_contributors=[
            "High memory usage may contribute to slowdowns"
        ],

        confirmed_findings=[
            "No confirmed cause of the slowdown was established"
        ],

        recommendations=[
            "Check which processes are consuming memory",
            "Review available storage"
        ]
    )

    print(response)