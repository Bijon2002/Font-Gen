from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from .config import CELL, CHARS


def build_ttf(cells: dict[str, object], family: str, output: str) -> None:
    builder = FontBuilder(1000, isTTF=True)
    builder.setupGlyphOrder([".notdef", "space"] + list(CHARS))
    builder.setupCharacterMap({ord(char): char for char in cells if char in CHARS})
    glyphs = {}
    metrics = {".notdef": (600, 0), "space": (350, 0)}

    empty_pen = TTGlyphPen(None)
    glyphs[".notdef"] = empty_pen.glyph()
    glyphs["space"] = TTGlyphPen(None).glyph()
    for character in CHARS:
        bitmap = cells.get(character)
        pen = TTGlyphPen(None)
        if bitmap is not None:
            import cv2
            import numpy as np

            contours, _ = cv2.findContours(bitmap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) < 8:
                    continue
                points = contour[:, 0, :]
                pen.moveTo((int(points[0][0] * 1000 / CELL), int((CELL - points[0][1]) * 1000 / CELL)))
                for point in points[1:]:
                    pen.lineTo((int(point[0] * 1000 / CELL), int((CELL - point[1]) * 1000 / CELL)))
                pen.closePath()
        glyphs[character] = pen.glyph()
        metrics[character] = (650, 0)

    builder.setupGlyf(glyphs)
    builder.setupHead(unitsPerEm=1000, flags=0x000B)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable(
        {
            "familyName": family,
            "styleName": "Regular",
            "fullName": f"{family} Regular",
            "psName": family.replace(" ", "") + "-Regular",
        }
    )
    builder.setupOS2(
        version=4,
        usWeightClass=400,
        usWidthClass=5,
        fsSelection=0x40,
        sTypoAscender=800,
        sTypoDescender=-200,
        usWinAscent=800,
        usWinDescent=200,
    )
    builder.setupPost(formatType=3.0)
    builder.save(output)
    font = TTFont(output)
    font.recalcBBoxes = True
    font.recalcTimestamp = False
    font.save(output)
