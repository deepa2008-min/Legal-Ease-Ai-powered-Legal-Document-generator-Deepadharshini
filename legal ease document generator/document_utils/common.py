import base64
import binascii
import re

from io import BytesIO

from PIL import Image


def sanitize_text(text: str) -> str:

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = text.replace(
        "\u2018",
        "'"
    )

    text = text.replace(
        "\u2019",
        "'"
    )

    text = text.replace(
        "\u201c",
        '"'
    )

    text = text.replace(
        "\u201d",
        '"'
    )

    text = text.replace(
        "\u2013",
        "-"
    )

    text = text.replace(
        "\u2014",
        "-"
    )

    text = text.replace(
        "\u00a0",
        " "
    )

    text = "".join(
        character
        for character in text
        if character in "\n\t"
        or ord(character) >= 32
    )

    return text.strip()


def safe_filename(value: str) -> str:

    value = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        value.strip()
    )

    return (
        value.strip("._")
        or "legal_document"
    )


def decode_logo(logo_base64: str | None):

    if not logo_base64:
        return None

    try:

        if "," in logo_base64:
            logo_base64 = logo_base64.split(
                ",",
                1
            )[1]

        raw = base64.b64decode(
            logo_base64,
            validate=True
        )

        image = Image.open(
            BytesIO(raw)
        )

        image.verify()

        return raw

    except (
        ValueError,
        binascii.Error,
        OSError
    ):

        return None