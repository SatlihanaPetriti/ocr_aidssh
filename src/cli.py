"""Command-line entry point.

Usage:
    python -m src.cli ocr <path-to-pdf-or-image> [--lang sqi] [--min-conf 40] [--no-clean]
                                                  [--pages 3,4,10-15] [--psm 6] [--dpi 300]
    python -m src.cli search <query>
    python -m src.cli correct <path-to-ocr-txt-file> [--model llama3.2:3b]
"""
import argparse
import difflib
from pathlib import Path

from PIL import Image

from src.config import DEFAULT_DPI, DEFAULT_LANG, DEFAULT_MIN_CONFIDENCE, PROJECT_ROOT
from src.correct.llm_correct import DEFAULT_MODEL, correct_text
from src.index.search_index import add_page, get_connection, search
from src.ocr.engine import ocr_image
from src.ocr.pdf_extract import parse_page_spec, pdf_pages_to_images
from src.ocr.preprocess import clean_for_ocr

DB_PATH = PROJECT_ROOT / "data" / "index.db"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def run_ocr(path: Path, lang: str, min_conf: int, clean: bool, page_spec: str | None, psm: int, dpi: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection(DB_PATH)

    if path.suffix.lower() == ".pdf":
        pages_to_render = parse_page_spec(page_spec) if page_spec else None
        pages = pdf_pages_to_images(path, dpi=dpi, pages=pages_to_render)
    else:
        pages = [(1, Image.open(path))]

    # Settings tag in the filename so different --psm/--dpi/--no-clean runs
    # land in separate files instead of overwriting each other — makes it
    # possible to compare configurations side by side.
    tag = f"psm{psm}_dpi{dpi}{'_raw' if not clean else ''}"

    for page_num, image in pages:
        if clean:
            image = clean_for_ocr(image)
        result = ocr_image(image, lang=lang, min_confidence=min_conf, psm=psm)

        out_file = OUTPUT_DIR / f"{path.stem}_p{page_num}_{tag}.txt"
        out_file.write_text(result.text, encoding="utf-8")

        add_page(conn, source_file=path.name, page_num=page_num, text=result.text, mean_confidence=result.mean_confidence)

        print(
            f"[{path.name} p{page_num} {tag}] fjale mbajtur: {result.kept_word_count}/{result.word_count} "
            f"(besueshmeri mesatare: {result.mean_confidence:.1f}) -> {out_file.name}"
        )


def run_search(query: str) -> None:
    conn = get_connection(DB_PATH)
    rows = search(conn, query)
    if not rows:
        print("Asnje rezultat.")
        return
    for row in rows:
        print(f"\n{row['source_file']} (faqe {row['page_num']}, besueshmeri {row['mean_confidence']:.1f})")
        print(f"  {row['snippet']}")


def run_correct(path: Path, model: str) -> None:
    original = path.read_text(encoding="utf-8")
    corrected = correct_text(original, model=model)

    out_file = path.with_name(f"{path.stem}_corrected{path.suffix}")
    out_file.write_text(corrected, encoding="utf-8")

    similarity = difflib.SequenceMatcher(None, original, corrected).ratio()
    print(
        f"[{path.name}] gjatesia: {len(original)} -> {len(corrected)} karaktere, "
        f"ngjashmeri me origjinalin: {similarity * 100:.1f}% -> {out_file.name}"
    )
    if similarity < 0.7:
        print("  KUJDES: ndryshim shume i madh nga origjinali — kontrolloje me kujdes, mund te kete 'halucinuar'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR + kerkim lokal per arkivin AIDSSH")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ocr_parser = subparsers.add_parser("ocr", help="Bej OCR nje PDF ose imazh")
    ocr_parser.add_argument("path", type=Path)
    ocr_parser.add_argument("--lang", default=DEFAULT_LANG)
    ocr_parser.add_argument("--min-conf", type=int, default=DEFAULT_MIN_CONFIDENCE)
    ocr_parser.add_argument("--no-clean", action="store_true", help="Kapërce pastrimin e imazhit")
    ocr_parser.add_argument("--pages", default=None, help='Vetem keto faqe nga nje PDF, p.sh. "3,4,10-15"')
    ocr_parser.add_argument("--psm", type=int, default=6, help="Tesseract page segmentation mode (provo 3, 4, 6, 11)")
    ocr_parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="DPI per nxjerrjen e faqeve nga PDF")

    search_parser = subparsers.add_parser("search", help="Kerko ne tekstin e OCR-uar")
    search_parser.add_argument("query")

    correct_parser = subparsers.add_parser("correct", help="Korrigjo gabime OCR me LLM lokal (Ollama)")
    correct_parser.add_argument("path", type=Path)
    correct_parser.add_argument("--model", default=DEFAULT_MODEL)

    args = parser.parse_args()

    if args.command == "ocr":
        run_ocr(
            args.path, lang=args.lang, min_conf=args.min_conf, clean=not args.no_clean,
            page_spec=args.pages, psm=args.psm, dpi=args.dpi,
        )
    elif args.command == "search":
        run_search(args.query)
    elif args.command == "correct":
        run_correct(args.path, model=args.model)


if __name__ == "__main__":
    main()
