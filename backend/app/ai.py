import os

import cv2
import numpy as np

from .config import CHARS

PROMPT = "Draw the missing alphabet in the same handwriting style as the uploaded template, black on white, in an 8 by 8 grid."
STYLE_PROMPT = (
    "The image shows some letters of a bold display font. Copy the exact style: shape, slant, sharp edges, thickness. "
    "Draw these 62 characters in that style as solid black shapes on a pure white background, flat, no color, no 3D, "
    "no shadow, in an 8 by 8 grid, no grid lines, each centered in its own equal square cell, left to right, top to bottom: "
    + CHARS
    + ". Last 2 cells empty."
)


def generate_missing_letters(image_bytes: bytes, prompt: str = PROMPT) -> bytes:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("AI completion requires the GEMINI_API_KEY environment variable.")
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")],
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    raise ValueError("The AI model did not return an image.")


def cells_from_ai(image_bytes: bytes, prompt: str = PROMPT) -> dict[str, np.ndarray]:
    sheet = generate_missing_letters(image_bytes, prompt)
    image = cv2.imdecode(np.frombuffer(sheet, np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("The AI response was not a readable image.")
    rows, columns = 8, 8
    height, width = image.shape
    cells = {}
    for index, character in enumerate(CHARS):
        row, column = divmod(index, columns)
        cells[character] = image[row * height // rows : (row + 1) * height // rows, column * width // columns : (column + 1) * width // columns]
    return cells


def complete_with_ai(known: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    if not known:
        raise ValueError("No letters were detected in the title image.")
    strip = np.hstack([255 - cell for cell in known.values()])
    ok, jpg = cv2.imencode(".jpg", strip)
    if not ok:
        raise ValueError("Could not prepare detected letters for AI completion.")
    cells = cells_from_ai(jpg.tobytes(), STYLE_PROMPT)
    cells.update(known)
    for character in CHARS:
        if character.islower() and character.upper() in cells:
            cells[character] = cells[character.upper()]
    return cells
