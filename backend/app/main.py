import os
import re
import tempfile

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from .fontbuild import build_ttf
from .style_image import cutout_png, known_cells
from .template import make_template
from .vision import extract_cells

app = FastAPI(title="FontGen")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def read_img(photo: UploadFile) -> tuple[bytes, np.ndarray]:
    data = photo.file.read()
    if len(data) > 10_000_000:
        raise HTTPException(413, "Image too large (max 10 MB).")
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Not a valid image.")
    return data, image


@app.get("/template")
def template() -> FileResponse:
    path = os.path.join(tempfile.gettempdir(), "fontgen_template.pdf")
    make_template(path)
    return FileResponse(path, media_type="application/pdf", filename="fontgen_template.pdf")


@app.post("/generate")
def generate(
    photo: UploadFile = File(...),
    name: str = Form("FontGen"),
    mode: str = Form("template"),
    text: str = Form(""),
    color: str = Form("#f5b800"),
) -> FileResponse:
    data, image = read_img(photo)
    if mode not in {"template", "ai", "style"}:
        raise HTTPException(422, "Mode must be template, ai, or style.")
    family = re.sub(r"[^A-Za-z0-9 ]", "", name).strip()[:30] or "FontGen"
    try:
        if mode == "style":
            from .ai import complete_with_ai

            cells = complete_with_ai(known_cells(image, text, color))
        elif mode == "ai":
            from .ai import cells_from_ai

            cells = cells_from_ai(data)
        else:
            cells = extract_cells(image)
        output = os.path.join(
            tempfile.gettempdir(),
            f"{family.replace(' ', '_')}_{os.urandom(8).hex()}.ttf",
        )
        build_ttf(cells, family, output)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return FileResponse(
        output,
        media_type="font/ttf",
        filename=f"{family.replace(' ', '_')}.ttf",
        headers={"Cache-Control": "no-store"},
    )


@app.post("/cutout")
def cutout(photo: UploadFile = File(...)) -> Response:
    _, image = read_img(photo)
    try:
        result = cutout_png(image)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return Response(result, media_type="image/png")
