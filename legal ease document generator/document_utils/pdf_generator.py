from io import BytesIO

from fpdf import FPDF

from .common import (
    decode_logo,
    sanitize_text
)


class LegalEasePDF(FPDF):

    def __init__(
        self,
        doc_type: str,
        logo_bytes=None
    ):

        super().__init__()

        self.doc_type = doc_type
        self.logo_bytes = logo_bytes

        self.set_auto_page_break(
            auto=True,
            margin=18
        )

    def header(self):

        if self.logo_bytes:

            try:

                self.image(
                    BytesIO(
                        self.logo_bytes
                    ),
                    x=95,
                    y=8,
                    w=20
                )

                self.ln(16)

            except Exception:
                pass

        self.set_font(
            "Helvetica",
            "B",
            12
        )

        self.cell(
            0,
            8,
            self.doc_type.upper(),
            align="C"
        )

        self.ln(8)

    def footer(self):

        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "",
            8
        )

        self.cell(
            0,
            8,
            "LegalEase - AI-generated draft | "
            "Review before legal use",
            align="C"
        )


def format_pdf(
    text: str,
    doc_type: str,
    logo_base64: str | None = None
) -> bytes:

    pdf = LegalEasePDF(
        doc_type,
        decode_logo(logo_base64)
    )

    pdf.add_page()

    clean_text = sanitize_text(text)

    for raw_line in clean_text.split("\n"):

        line = raw_line.strip()

        if not line:

            pdf.ln(3)

            continue

        upper = line.upper()

        is_heading = (
            len(line) < 90
            and (
                upper == line
                or upper.startswith("SECTION ")
                or upper.startswith("ARTICLE ")
                or upper.startswith("PARTIES")
                or upper.startswith("TERMS")
                or upper.startswith("SIGNATURE")
                or upper.startswith("DRAFT NOTICE")
                or upper.startswith("GENERAL PROVISIONS")
                or upper.startswith("BACKGROUND")
                or upper.startswith("JURISDICTION")
            )
        )

        if is_heading:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                7,
                line
            )

            pdf.ln(1)

        else:

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            pdf.multi_cell(
                0,
                6,
                line
            )

            pdf.ln(1)

    pdf.ln(4)

    pdf.set_font(
        "Helvetica",
        "I",
        8
    )

    pdf.multi_cell(
        0,
        5,
        "Draft notice: This document is generated "
        "for educational/informational use and "
        "should be reviewed by a qualified legal "
        "professional."
    )

    return bytes(
        pdf.output()
    )