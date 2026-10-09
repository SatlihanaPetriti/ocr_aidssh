"""Llogarit CER/WER te daljes se OCR-it kundrejt tekstit te sakte (data/ground_truth/).

Perdorim:
    python scripts/evaluate.py [--tag psm6_dpi300]

Per cdo data/ground_truth/<emri>.txt kerkon data/output/<emri>_p1_<tag>.txt.
Hapesirat dhe ndarjet e rreshtave injorohen; shkronjat krahasohen sic jane.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRUTH_DIR = ROOT / "data" / "ground_truth"
OUTPUT_DIR = ROOT / "data" / "output"


def edit_distance(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def normalize(text: str) -> str:
    # Bashkon fjalet e ndara me vizeze ne fund te rreshtit ("Popu-\nllor" -> "Popullor").
    return " ".join(text.replace("-\n", "").split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="psm6_dpi300")
    args = parser.parse_args()

    total_char_err = total_chars = total_word_err = total_words = 0
    print(f"{'faqe':<10} {'CER':>7} {'WER':>7}")
    for truth_file in sorted(TRUTH_DIR.glob("*.txt")):
        out_file = OUTPUT_DIR / f"{truth_file.stem}_p1_{args.tag}.txt"
        if not out_file.exists():
            print(f"{truth_file.stem:<10} (mungon {out_file.name})")
            continue
        truth = normalize(truth_file.read_text(encoding="utf-8"))
        ocr = normalize(out_file.read_text(encoding="utf-8"))
        if not truth:
            print(f"{truth_file.stem:<10} faqe e zbrazet: {len(ocr)} karaktere te tepert (jo ne totale)")
            continue
        char_err = edit_distance(list(truth), list(ocr))
        word_err = edit_distance(truth.split(), ocr.split())
        n_words = len(truth.split())
        print(f"{truth_file.stem:<10} {char_err / len(truth):>6.1%} {word_err / n_words:>6.1%}")
        total_char_err += char_err
        total_chars += len(truth)
        total_word_err += word_err
        total_words += n_words

    if total_chars:
        print(f"{'GJITHSEJ':<10} {total_char_err / total_chars:>6.1%} {total_word_err / total_words:>6.1%}")


if __name__ == "__main__":
    main()
