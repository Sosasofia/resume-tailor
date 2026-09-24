from app.domain.profile import (
    Basics,
    Experience,
    ResumeProfile,
)

class FakeResponse:
    def __init__(self, result):
        self.output_parsed = result


class FakeResponses:
    def __init__(self, result):
        self.result = result

    def parse(self, **kwargs):
        return FakeResponse(self.result)


class FakeClient:
    def __init__(self, result):
        self.responses = FakeResponses(result)


def make_profile() -> ResumeProfile:
    return ResumeProfile(
        basics=Basics(
            name="Victor Vigon",
            location="Buenos Aires, Argentina",
            email="victor@example.com",
        ),
        summary="Backend developer",
        skills=["Python", "SQL", "Docker"],
        experience=[
            Experience(
                company="Nutbank",
                role="Back End Developer",
                location="Argentina",
                start_year=2020,
                end_year=2024,
                achievements=[
                    "Designed and developed a microservices architecture.",
                ],
            )
        ],
        projects=[],
        education=[],
    )