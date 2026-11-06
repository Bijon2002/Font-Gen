from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .config import CHARS


def make_template(path: str) -> None:
    page_width, page_height = A4
    pdf = canvas.Canvas(path, pagesize=A4)
    pdf.setTitle("FontGen handwriting template")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, page_height - 48, "FontGen handwriting template")
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, page_height - 66, "Fill each box with one centered character, then photograph the page.")

    cell = 34
    left = 40
    top = page_height - 100
    for index, character in enumerate(CHARS):
        row, column = divmod(index, 12)
        x = left + column * cell
        y = top - (row + 1) * cell
        pdf.rect(x, y, cell, cell)
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(x + cell / 2, y + 4, character)

    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(40, 42, "Use a flat, well-lit photo with the whole template visible.")
    pdf.save()
