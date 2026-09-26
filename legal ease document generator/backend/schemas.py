from typing import List

from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000
    )

    terms: List[str] = Field(
        default_factory=list,
        max_length=50
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    jurisdiction: str = Field(
        default="India",
        max_length=200
    )

    additional_instructions: str = Field(
        default="",
        max_length=5000
    )

    logo_base64: str | None = None

    @field_validator("terms")
    @classmethod
    def clean_terms(cls, value):
        cleaned = []

        for term in value:
            if term and term.strip():
                cleaned.append(term.strip())

        return cleaned


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str
    mock_mode: bool


class ExportRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=100000
    )

    logo_base64: str | None = None