from PyPDF2 import PdfReader
import svgwrite

reader = PdfReader("en/solution/solution_12345.pdf")
page = reader.pages[0]

dwg = svgwrite.Drawing("Extract_text_rect.svg", profile="tiny")


def visitor_svg_rect(op, args, cm, tm):
    if op == b"re":
        (x, y, w, h) = (args[i].as_numeric() for i in range(4))
        dwg.add(dwg.rect((x, y), (w, h), stroke="red", fill_opacity=0.05))


def visitor_svg_text(text, cm, tm, fontDict, fontSize):
    (x, y) = (tm[4], tm[5])
    dwg.add(dwg.text(text, insert=(x, y), fill="blue"))


page.extract_text(
    visitor_operand_after=visitor_svg_rect, visitor_text=visitor_svg_text
)
dwg.save()