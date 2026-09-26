import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class GenerationResult:
    text: str
    model: str
    mock_mode: bool


class GeminiDocumentGenerator:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        ).strip()

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        ).strip()

        self.mock_mode = (
            os.getenv("MOCK_AI", "").lower() == "true"
            or not self.api_key
        )

        self._client = None

        if not self.mock_mode:

            from google import genai

            self._client = genai.Client(
                api_key=self.api_key
            )

    def _build_prompt(
        self,
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction,
        additional_instructions
    ):

        term_lines = "\n".join(
            f"- {term}"
            for term in terms
        )

        if not term_lines:
            term_lines = "- No specific terms supplied."

        prompt = f"""
You are a legal-document drafting assistant
for an educational software project.

Create a professional DRAFT of the requested
legal document.

IMPORTANT RULES:

1. Do not invent facts.
2. Do not invent party information.
3. Do not claim that this is lawyer-reviewed.
4. Use placeholders when information is missing.
5. Use clear numbered sections.
6. Preserve supplied names and dates.
7. Include signature sections.
8. Include a Draft Notice.
9. Return plain text only.
10. Do not use Markdown code fences.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

JURISDICTION:
{jurisdiction}

TERMS:

{term_lines}

ADDITIONAL INSTRUCTIONS:

{additional_instructions or "None"}

Create the document with:

1. Title
2. Parties
3. Effective date
4. Background
5. Definitions if necessary
6. Main clauses
7. Responsibilities
8. Payment or consideration where applicable
9. Termination where applicable
10. Confidentiality where applicable
11. Governing law
12. Dispute resolution
13. Signature blocks
14. Draft Notice

The Draft Notice should state that this
is an AI-generated draft for educational/
informational purposes and should be reviewed
by a qualified legal professional.
"""

        return prompt.strip()

    def _mock_document(
        self,
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction
    ):

        term_lines = "\n".join(
            f"{index}. {term}"
            for index, term in enumerate(
                terms,
                start=1
            )
        )

        if not term_lines:
            term_lines = "1. [No specific terms supplied.]"

        return f"""
{document_type.upper()}

This draft is made effective as of
{effective_date}.

PARTIES

{parties}

JURISDICTION

{jurisdiction}

BACKGROUND

The parties intend to enter into this
{document_type} according to the information
supplied by the user.

TERMS AND CONDITIONS

{term_lines}

GENERAL PROVISIONS

1. The parties agree to perform their
respective obligations in good faith.

2. Any amendment should be recorded in
writing and accepted by the parties.

3. If a provision is found unenforceable,
the remaining provisions should continue
to the extent permitted by applicable law.

4. Governing law and dispute-resolution
provisions should be reviewed and completed
for the applicable jurisdiction.

SIGNATURES

Party 1:

Signature: ______________________________

Name: __________________________________

Date: ___________________________________


Party 2:

Signature: ______________________________

Name: __________________________________

Date: ___________________________________


DRAFT NOTICE

This document is an AI-generated draft
for educational and informational purposes.

It has not been reviewed by a qualified
legal professional and should be checked
for jurisdiction-specific requirements
before use.
""".strip()

    def generate_document(
        self,
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction,
        additional_instructions=""
    ):

        if self.mock_mode:

            return GenerationResult(
                text=self._mock_document(
                    document_type,
                    parties,
                    terms,
                    effective_date,
                    jurisdiction
                ),
                model="mock",
                mock_mode=True
            )

        prompt = self._build_prompt(
            document_type,
            parties,
            terms,
            effective_date,
            jurisdiction,
            additional_instructions
        )

        try:

            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            text = getattr(
                response,
                "text",
                None
            )

            if not text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return GenerationResult(
                text=text.strip(),
                model=self.model,
                mock_mode=False
            )

        except Exception as exc:

            fallback = self._mock_document(
                document_type,
                parties,
                terms,
                effective_date,
                jurisdiction
            )

            fallback += (
                "\n\nAI SERVICE NOTE\n"
                f"Gemini request failed: "
                f"{type(exc).__name__}. "
                "The fallback draft was returned."
            )

            return GenerationResult(
                text=fallback,
                model=self.model,
                mock_mode=True
            )