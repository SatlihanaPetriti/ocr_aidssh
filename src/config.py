from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESSDATA_DIR = PROJECT_ROOT / "tessdata"
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DEFAULT_LANG = "sqi"
DEFAULT_DPI = 300
DEFAULT_MIN_CONFIDENCE = 40
