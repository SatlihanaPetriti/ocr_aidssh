"""Gjeneron nje raport HTML lokal: ground truth krah daljes se Tesseract dhe EasyOCR, me dallimet te theksuara.

Perdorim: python scripts/diff_report.py   -> data/output_vjeter/diff_report.html
Raporti permban tekst real arkivi: mbetet lokal (data/output_vjeter/ eshte ne .gitignore), mos e ngarko askund.
"""
import difflib
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import edit_distance, normalize

D = Path(__file__).resolve().parent.parent / "data"
PAGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19]
SOURCES = {
    "Tesseract": lambda p: D / "output" / f"1 ({p})_p1_psm6_dpi300.txt",
    "EasyOCR": lambda p: D / "output_vjeter" / "easyocr" / f"1 ({p})_conf0.0.txt",
}


def render(truth_words, ocr_words):
    """Kthen HTML te daljes se OCR-it: fjale te gabuara (portokalli), te tepert (jeshile), te humbura (e kuqe, e kryqezuar)."""
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, truth_words, ocr_words, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(html.escape(" ".join(ocr_words[j1:j2])))
        elif op == "replace":
            out.append(f'<span class="w">{html.escape(" ".join(ocr_words[j1:j2]))}</span>')
            out.append(f'<span class="m" title="duhej">{html.escape(" ".join(truth_words[i1:i2]))}</span>')
        elif op == "insert":
            out.append(f'<span class="x">{html.escape(" ".join(ocr_words[j1:j2]))}</span>')
        else:
            out.append(f'<span class="m">{html.escape(" ".join(truth_words[i1:i2]))}</span>')
    return " ".join(out)


sections, nav = [], []
for p in PAGES:
    truth = normalize((D / "ground_truth" / f"1 ({p}).txt").read_text(encoding="utf-8"))
    cols = [f'<div><h3>Teksti i sakte</h3><p>{html.escape(truth) or "<i>(faqe e zbrazet)</i>"}</p></div>']
    badges = []
    for name, path_of in SOURCES.items():
        f = path_of(p)
        ocr = normalize(f.read_text(encoding="utf-8")) if f.exists() else ""
        cer = f"{edit_distance(list(truth), list(ocr)) / len(truth):.1%}" if truth else f"{len(ocr)} kar. te tepert"
        badges.append(f"{name} {cer}")
        cols.append(f"<div><h3>{name} <small>CER {cer}</small></h3><p>{render(truth.split(), ocr.split())}</p></div>")
    nav.append(f'<a href="#p{p}">{p}</a>')
    sections.append(f'<section id="p{p}"><h2>Faqja 1 ({p}) <small>{" · ".join(badges)}</small></h2><div class="cols">{"".join(cols)}</div></section>')

page = f"""<!doctype html><html lang="sq"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Raport OCR</title><style>
:root{{--bg:#fff;--fg:#1a1a1a;--mut:#666;--line:#ddd;--w:#ffe0b2;--x:#c8e6c9;--m:#ffcdd2}}
@media (prefers-color-scheme:dark){{:root{{--bg:#16181b;--fg:#e8e8e8;--mut:#9aa;--line:#333;--w:#6b4a12;--x:#27552b;--m:#6d2a30}}}}
body{{margin:0 auto;max-width:1400px;padding:16px;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,sans-serif}}
nav{{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:8px}}
nav a{{color:inherit;padding:2px 8px;border:1px solid var(--line);border-radius:6px;text-decoration:none}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px}}
h2{{margin:28px 0 8px}} h3{{margin:0 0 6px}} small{{color:var(--mut);font-weight:400}}
p{{margin:0;white-space:pre-wrap;word-break:break-word}}
.w{{background:var(--w)}} .x{{background:var(--x)}} .m{{background:var(--m);text-decoration:line-through}}
.legend span{{padding:1px 6px;margin-right:8px;border-radius:4px}}
</style></head><body>
<h1>Ground truth kundrejt OCR</h1>
<p class="legend"><span class="w">fjale e gabuar</span><span class="x">e tepert (OCR e shtoi)</span><span class="m">e humbur (duhej, shfaqet e kryqezuar)</span></p>
<nav>{"".join(nav)}</nav>{"".join(sections)}</body></html>"""

out = D / "output_vjeter" / "diff_report.html"
out.write_text(page, encoding="utf-8")
print(out)
