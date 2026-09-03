from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_rejects_empty_file() -> None:
    response = client.post(
        "/extract",
        files={
            "document": (
                "resume.pdf",
                b"",
                "application/pdf",
            )
        },
        data={
            "document_type": "resume",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded document is empty."