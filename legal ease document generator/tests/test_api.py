import os

os.environ["MOCK_AI"] = "true"

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["name"] == "LegalEase"


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_generate():

    payload = {

        "document_type":
            "Lease Agreement",

        "parties":
            "Alice (Tenant), Bob (Landlord)",

        "terms": [
            "Rent is INR 10000",
            "Deposit is INR 20000"
        ],

        "effective_date":
            "2026-10-01",

        "jurisdiction":
            "Tamil Nadu, India",

        "additional_instructions":
            "Use numbered clauses"
    }


    response = client.post(
        "/generate",
        json=payload
    )


    assert response.status_code == 200


    data = response.json()


    assert (
        data["document_type"]
        == "Lease Agreement"
    )


    assert (
        "LEASE AGREEMENT"
        in data["content"]
    )


def test_export_txt():

    payload = {

        "document_type":
            "NDA",

        "content":
            "CONFIDENTIALITY AGREEMENT\n"
            "Party A and Party B"
    }


    response = client.post(
        "/export/txt",
        json=payload
    )


    assert response.status_code == 200

    assert (
        b"CONFIDENTIALITY"
        in response.content
    )


def test_export_docx():

    payload = {

        "document_type":
            "NDA",

        "content":
            "CONFIDENTIALITY AGREEMENT\n"
            "Party A and Party B"
    }


    response = client.post(
        "/export/docx",
        json=payload
    )


    assert response.status_code == 200

    # DOCX is a ZIP-based file.
    assert response.content[:2] == b"PK"


def test_export_pdf():

    payload = {

        "document_type":
            "NDA",

        "content":
            "CONFIDENTIALITY AGREEMENT\n"
            "Party A and Party B"
    }


    response = client.post(
        "/export/pdf",
        json=payload
    )


    assert response.status_code == 200

    assert response.content.startswith(
        b"%PDF"
    )