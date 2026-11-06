import cv2
import numpy as np

from .config import BASE, CELL, PAD


def face_mask(image: np.ndarray, hex_color: str, tol: int = 18) -> np.ndarray:
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith("#"):
        raise ValueError("Color must be a hexadecimal value such as #f5b800.")
    try:
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    except ValueError as exc:
        raise ValueError("Color must be a hexadecimal value such as #f5b800.") from exc
    h, s, v = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
    lower = (max(int(h) - tol, 0), max(int(s) - 80, 40), max(int(v) - 80, 60))
    upper = (min(int(h) + tol, 179), 255, 255)
    mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), lower, upper)
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))


def split_letters(mask: np.ndarray) -> list[np.ndarray]:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    area_column = 4
    x_column = 0
    ids = [i for i in range(1, count) if stats[i, area_column] > 0.002 * mask.size]
    ids.sort(key=lambda i: stats[i, x_column])
    return [(labels == i).astype(np.uint8) * 255 for i in ids]


def to_cell(mask: np.ndarray) -> np.ndarray:
    x, y, width, height = cv2.boundingRect(mask)
    glyph = mask[y : y + height, x : x + width]
    scale = min(0.6 * CELL / height, (CELL - 2 * PAD - 4) / width)
    glyph = cv2.resize(glyph, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    glyph = (glyph > 127).astype(np.uint8) * 255
    cell = np.zeros((CELL, CELL), np.uint8)
    top, left = int(BASE) - glyph.shape[0], (CELL - glyph.shape[1]) // 2
    cell[top : top + glyph.shape[0], left : left + glyph.shape[1]] = glyph
    return cell


def known_cells(image: np.ndarray, text: str, color: str) -> dict[str, np.ndarray]:
    letters = [character for character in text.upper() if character.isalnum()]
    if not letters:
        raise ValueError("Enter the letters shown in the title image.")
    parts = split_letters(face_mask(image, color))
    if len(parts) != len(letters):
        raise ValueError(f"Found {len(parts)} shapes but you typed {len(letters)} letters. Re-pick the color or use a cleaner image.")
    return {character: to_cell(part) for character, part in zip(letters, parts)}


def cutout_png(image: np.ndarray) -> bytes:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    yellow = cv2.inRange(hsv, (18, 120, 150), (35, 255, 255))
    teal = cv2.inRange(hsv, (80, 80, 40), (100, 255, 255))
    red = cv2.inRange(hsv, (0, 120, 40), (10, 255, 255)) | cv2.inRange(hsv, (170, 120, 40), (180, 255, 255))
    alpha = cv2.morphologyEx(yellow | teal | red, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    ok, encoded = cv2.imencode(".png", np.dstack([image, alpha]))
    if not ok:
        raise ValueError("Could not encode the transparent PNG.")
    return encoded.tobytes()
