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

    notdef_pen = TTGlyphPen(None)
    notdef_pen.moveTo((80, 0))
    notdef_pen.lineTo((520, 0))
    notdef_pen.lineTo((520, 700))
    notdef_pen.lineTo((80, 700))
    notdef_pen.closePath()
    glyphs[".notdef"] = notdef_pen.glyph()
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
        metrics[character] = (1000 + len(metrics), 0)

    builder.setupGlyf(glyphs)
    builder.setupHead(unitsPerEm=1000, flags=0x0003)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(
        ascent=800,
        descent=-200,
        lineGap=0,
        numberOfHMetrics=len(metrics),
    )
    builder.setupNameTable(
        {
            "familyName": family,
            "styleName": "Regular",
            "fullName": f"{family} Regular",
            "psName": family.replace(" ", "") + "-Regular",
        }
    )
    builder.setupOS2(
        version=3,
        fsType=0,
        usWeightClass=400,
        usWidthClass=5,
        fsSelection=0x40,
        sTypoAscender=800,
        sTypoDescender=-200,
        usWinAscent=800,
        usWinDescent=200,
    )
    builder.setupPost(formatType=2.0)
    builder.save(output)
    font = TTFont(output, recalcBBoxes=True, recalcTimestamp=False)
    font.flavor = None
    font["OS/2"].fsType = 0
    font["head"].flags = 0x000B
    font["OS/2"].achVendID = "FONT"
    font["hhea"].numberOfHMetrics = len(font["hmtx"].metrics)
    font.recalcBBoxes = True
    font.recalcTimestamp = False
    font.save(output)
    validated = TTFont(output, checkChecksums=1)
    validated["hhea"].numberOfHMetrics = len(validated["hmtx"].metrics)
    validated.recalcBBoxes = False
    validated.recalcTimestamp = False
    validated.save(output)
    validated = TTFont(output, checkChecksums=1)
    if len(validated.getBestCmap()) != len(cells):
        raise ValueError("The generated font failed validation. Please try again.")
