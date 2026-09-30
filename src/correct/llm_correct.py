"""Conservative OCR-error cleanup using a local LLM via Ollama.

Talks only to http://localhost:11434 (Ollama's local HTTP API) — nothing
ever leaves the machine. The prompt is deliberately strict: fix obvious
character-level OCR mistakes, never invent or reinterpret content. LLMs
can still hallucinate, so this should be treated as a "readable copy" for
search/summaries, not a replacement for the raw OCR text (which is always
kept alongside, never overwritten).
"""
import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """Je nje asistent qe korrigjon VETEM gabime karakteresh nga OCR ne tekst shqip te vjeter (dokumente arkivi, makine shkrimi).

RREGULLA TE RREPTA - ndiqi pa perjashtim:
1. Korrigjo VETEM gabime te qarta shkronjash brenda nje fjale (karaktere te ngaterruara qe e bejne fjalen te mos ekzistoje ne shqip, kur konteksti tregon qarte cila fjale duhej te ishte).
2. MOS shto, hiq, apo ndrysho asnje fjale, emer, date, numer, apo shenje pikesimi qe e kupton qarte ashtu sic eshte.
3. MOS e ndrysho kuptimin, renditjen, apo strukturen e fjalise ne asnje menyre.
4. Nese nje fjale/emer/numer eshte i paqarte ose s'je i sigurt cfare duhej te ishte, LERE EKZAKTESISHT ashtu sic eshte ne origjinal — mos hamendëso.
5. Pergjigju VETEM me tekstin e korrigjuar. Asnje koment, asnje shpjegim, asnje hyrje si "Ja teksti i korrigjuar:" — vetem teksti, fjale per fjale i njejte nga gjatesia me origjinalin perveq korrigjimeve te shkronjave."""


def correct_text(text: str, model: str = DEFAULT_MODEL, timeout: int = 300) -> str:
    # Cap output length relative to input so a confused model can't ramble
    # on indefinitely instead of stopping — small models sometimes do this,
    # which is what made early tests hang for minutes on this CPU-only machine.
    max_tokens = max(64, int(len(text.split()) * 2.5) + 50)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": max_tokens},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["message"]["content"].strip()
