# AIDSSH OCR

Pipeline lokal (on-premise) per OCR + kerkim mbi arkivat e shtypshkruara te AIDSSH.

## Parime

- **Gjithcka xhiron lokalisht.** Asnje dokument real i arkivit nuk duhet t'i kaloje ndonje sherbimi cloud (perfshire asistentet AI si Claude). Kodi ketu perdor vetem Tesseract lokal dhe SQLite lokale.
- **Vetem shtypshkronja.** Dokumentet jane mix shkrim-dore + shtypshkronje; filtrimi bazohet fillimisht ne besueshmerine (confidence) e Tesseract-it — fjalet me confidence te ulet (tipike per shkrim dore) hidhen poshte. Kjo eshte nje heuristike e thjeshte, jo nje klasifikues — duhet vleresuar ne mostra reale.
- **OCR-i behet nga ne**, jo duke u mbeshtetur te layer-i ekzistues i Adobe Acrobat — ne mostren e pare qe u testua, ai dilte i papërdorshëm (karaktere te gabuara, fjale te shkaterruara).

## Setup

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

Tesseract OCR eshte instaluar ne `C:\Program Files\Tesseract-OCR\`. Modelet e gjuhes (shqip/anglisht/osd, "best" — me te sakta, jo me te shpejtat) jane ne `tessdata/` te ketij projekti, ne menyre qe te mos duhet admin per t'i shtuar/hequr.

## Perdorim

```powershell
# OCR mbi nje PDF (nxjerr .txt per faqe ne data/output/, indekson ne data/index.db)
.\venv\Scripts\python -m src.cli ocr "data\samples\dokument.pdf"

# OCR mbi nje imazh te vogel (p.sh. screenshot ~600 px i nje faqeje): zmadhoje 3 here para OCR-it
.\venv\Scripts\python -m src.cli ocr "data\samples\screenshot.png" --upscale 3

# Kerkim mbi tekstin e indeksuar
.\venv\Scripts\python -m src.cli search "fjala e kerkuar"
```

Vendos mostrat reale te testimit vetem ne `data/samples/` — ky folder eshte ne `.gitignore`, s'do commit-ohet kurre.

## Cfare mungon ende (fazat e ardhshme)

- **Filtrim me i mire shtypshkronje/dore**: nese filtrimi vetem me confidence del i pamjaftueshem, hapi tjeter eshte layout/segmentation e rajoneve para OCR-it.
- **Summarization (sum-up)**: do kerkoje LLM lokal (p.sh. Ollama) — asnje API cloud, per te ruajtur konfidencialitetin.
- **Integrim me e-study**: forma ende e papercaktuar — API lokale mbi indeksin e kerkimit eshte pika me e mundshme e nisjes.
