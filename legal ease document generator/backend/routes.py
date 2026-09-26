from fastapi import (
    APIRouter,
    HTTPException
)

from fastapi.responses import Response

from ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from document_utils.docx_generator import (
    format_docx
)

from document_utils.pdf_generator import (
    format_pdf
)

from document_utils.txt_generator import (
    format_txt
)

from .schemas import (
    DocumentRequest,
    DocumentResponse,
    ExportRequest
)


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        result = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            additional_instructions=(
                request.additional_instructions
            )
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=result.text,
            model=result.model,
            mock_mode=result.mock_mode
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.post("/export/txt")
def export_txt(
    request: ExportRequest
):

    content = format_txt(
        request.content
    )

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition":
            'attachment; filename="legal_document.txt"'
        }
    )


@router.post("/export/docx")
def export_docx(
    request: ExportRequest
):

    content = format_docx(
        request.content,
        request.document_type,
        request.logo_base64
    )

    return Response(
        content=content,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        headers={
            "Content-Disposition":
            'attachment; filename="legal_document.docx"'
        }
    )


@router.post("/export/pdf")
def export_pdf(
    request: ExportRequest
):

    content = format_pdf(
        request.content,
        request.document_type,
        request.logo_base64
    )

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            'attachment; filename="legal_document.pdf"'
        }
    )