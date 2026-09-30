"""Tesseract wrapper: OCR an image and keep only text Tesseract is confident about.

Confidence filtering is our first line of defense against handwriting: a model
trained on typed text tends to emit low-confidence garbage for handwritten
strokes, so dropping low-confidence words is a cheap way to keep mostly the
typewritten content. It is a heuristic, not a classifier — verify results on
real samples before trusting it for a whole archive.
"""
import re
from dataclasses import dataclass

import pytesseract
from PIL import Image

from src.config import DEFAULT_LANG, DEFAULT_MIN_CONFIDENCE, TESSDATA_DIR, TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
_TESSDATA_CONFIG = f'--tessdata-dir {TESSDATA_DIR}'

# Tokens with no letter or digit at all (just punctuation/symbols) are almost
# always noise picked up from stamps, seals, or scan artifacts, not real text.
_HAS_ALNUM = re.compile(r'[^\W_]', re.UNICODE)


@dataclass
class OcrResult:
    text: str
    mean_confidence: float
    word_count: int
    kept_word_count: int


def ocr_image(
    image: Image.Image,
    lang: str = DEFAULT_LANG,
    min_confidence: int = DEFAULT_MIN_CONFIDENCE,
    psm: int = 6,
) -> OcrResult:
    config = f'{_TESSDATA_CONFIG} --psm {psm}'
    data = pytesseract.image_to_data(
        image, lang=lang, config=config, output_type=pytesseract.Output.DICT,
    )

    lines: dict[tuple[int, int, int], list[str]] = {}
    confidences: list[float] = []
    total_words = 0

    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue
        total_words += 1
        if not _HAS_ALNUM.search(word):
            continue
        conf = float(data["conf"][i])
        if conf < min_confidence:
            continue
        confidences.append(conf)
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append(word)

    text = "\n".join(" ".join(words) for words in lines.values())
    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0

    return OcrResult(
        text=text,
        mean_confidence=mean_conf,
        word_count=total_words,
        kept_word_count=len(confidences),
    )
