"""Teston rregulla per zgjedhjen automatike Tesseract vs EasyOCR per faqe (pa ground truth gjate zgjedhjes).

Rregulli 'lexicon': vlereson cdo dalje me perqindjen e fjaleve qe gjenden ne fjalorin e ndertuar nga
ground truth i faqeve te TJERA (leave-one-out, pa rrjedhje). 'wordlike': perqindja e karaktereve ne
fjale qe duken si fjale (>=3 shkronja, me zanore).
Perdorim: python scripts/combine_engines.py   (kerkon data/output/ per Tesseract dhe data/output_vjeter/easyocr/)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import edit_distance, normalize

D = Path(__file__).resolve().parent.parent / "data"
PAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19]
TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)


def words(text):
    return [w.lower() for w in TOKEN.findall(text)]


def wordlike(text):
    ws = [w for w in words(text) if len(w) >= 3 and re.search(r"[aeiouyëAEIOUY]", w)]
    total = sum(len(w) for w in words(text))
    return sum(len(w) for w in ws) / total if total else 0.0


def lexicon_score(text, vocab):
    ws = words(text)
    return sum(w in vocab for w in ws) / len(ws) if ws else 0.0


truth = {p: normalize((D / "ground_truth" / f"1 ({p}).txt").read_text(encoding="utf-8")) for p in PAGES}
tess = {p: normalize((D / "output" / f"1 ({p})_p1_psm6_dpi300.txt").read_text(encoding="utf-8")) for p in PAGES}
easy = {p: normalize((D / "output_vjeter" / "easyocr" / f"1 ({p})_conf0.0.txt").read_text(encoding="utf-8")) for p in PAGES}

def cer(p, t):
    return edit_distance(list(truth[p]), list(t)) / len(truth[p])

tot = {k: [0, 0] for k in ("tesseract", "easyocr", "oracle", "wordlike", "lexicon")}
print(f"{'faqe':<5}{'tess':>7}{'easy':>7}  {'wordlike':>9}{'lexicon':>9}")
for p in PAGES:
    vocab = {w for q in PAGES if q != p for w in words(truth[q])}
    ct, ce = cer(p, tess[p]), cer(p, easy[p])
    pick_w = "tess" if wordlike(tess[p]) >= wordlike(easy[p]) else "easy"
    pick_l = "tess" if lexicon_score(tess[p], vocab) >= lexicon_score(easy[p], vocab) else "easy"
    n = len(truth[p])
    for k, c in (("tesseract", ct), ("easyocr", ce), ("oracle", min(ct, ce)),
                 ("wordlike", ct if pick_w == "tess" else ce), ("lexicon", ct if pick_l == "tess" else ce)):
        tot[k][0] += c * n; tot[k][1] += n
    print(f"{p:<5}{ct:>7.1%}{ce:>7.1%}  {pick_w:>9}{pick_l:>9}")
for k, (e, n) in tot.items():
    print(f"{k:<10} CER total {e / n:.1%}")
