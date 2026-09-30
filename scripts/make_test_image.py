"""Gjeneron nje imazh testimi (tekst shqip fiktiv, jo nga arkivi) per smoke-test te pipeline-it."""
from PIL import Image, ImageDraw, ImageFont

text = (
    "Ky eshte nje dokument testimi.\n"
    "Qellimi i ketij projekti eshte te lehtesoje kerkimin\n"
    "neper faqe te arkivit dhe te krijoje permbledhje.\n"
    "Shkronja te vecanta: e, c, GJUHESI.\n"
)

img = Image.new("RGB", (900, 300), color="white")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("C:/Windows/Fonts/cour.ttf", 24)
draw.multiline_text((30, 30), text, fill="black", font=font, spacing=12)
img.save("data/samples/test_synthetic.png")
print("Saved data/samples/test_synthetic.png")
