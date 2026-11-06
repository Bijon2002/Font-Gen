import cv2
import numpy as np

from .config import BASE, CELL, CHARS, PAD


def _normalize_cell(cell: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY) if cell.ndim == 3 else cell
    ink = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)[1]
    contours, _ = cv2.findContours(ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if cv2.contourArea(c) > 4]
    if not contours:
        return np.zeros((CELL, CELL), np.uint8)
    x, y, width, height = cv2.boundingRect(np.vstack(contours))
    glyph = ink[y : y + height, x : x + width]
    scale = min((CELL - 2 * PAD) / width, (BASE - PAD) / height)
    glyph = cv2.resize(glyph, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    result = np.zeros((CELL, CELL), np.uint8)
    top = BASE - glyph.shape[0]
    left = (CELL - glyph.shape[1]) // 2
    result[top : top + glyph.shape[0], left : left + glyph.shape[1]] = glyph
    return result


def extract_cells(image: np.ndarray) -> dict[str, np.ndarray]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold = cv2.threshold(gray, 190, 255, cv2.THRESH_BINARY_INV)[1]
    contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        if 20 <= width <= image.shape[1] / 3 and 20 <= height <= image.shape[0] / 3:
            boxes.append((x, y, width, height))
    if len(boxes) < len(CHARS):
        raise ValueError(f"Could not find all {len(CHARS)} template cells in the image.")
    boxes.sort(key=lambda box: (box[1] // max(box[3], 1), box[0]))
    cells: dict[str, np.ndarray] = {}
    for character, (x, y, width, height) in zip(CHARS, boxes[: len(CHARS)]):
        margin = max(2, int(min(width, height) * 0.08))
        cells[character] = _normalize_cell(image[y + margin : y + height - margin, x + margin : x + width - margin])
    return cells
