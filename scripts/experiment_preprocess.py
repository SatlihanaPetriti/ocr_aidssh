import sys, time
sys.path.insert(0, r"C:\Users\ACER\OneDrive\Desktop\ocr_aidssh")
sys.path.insert(0, r"C:\Users\ACER\OneDrive\Desktop\ocr_aidssh\scripts")
from pathlib import Path
import cv2, numpy as np
from PIL import Image
from evaluate import edit_distance, normalize
from src.ocr.engine import ocr_image
from src.ocr.preprocess import clean_for_ocr, _deskew

ROOT = Path(r"C:\Users\ACER\OneDrive\Desktop\ocr_aidssh\data")

def to_gray(im): return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
def pil(a): return Image.fromarray(a)

def bgnorm(gray):
    bg = cv2.medianBlur(cv2.dilate(gray, np.ones((15,15),np.uint8)), 51)
    return cv2.normalize(cv2.divide(gray, bg, scale=255), None, 0, 255, cv2.NORM_MINMAX)

def v_raw(im): return im
def v_gray(im): return pil(to_gray(im))
def v_clahe(im): return pil(cv2.createCLAHE(2.0,(8,8)).apply(to_gray(im)))
def v_bgnorm(im): return pil(bgnorm(to_gray(im)))
def v_bgnorm_otsu(im):
    g = bgnorm(to_gray(im)); return pil(cv2.threshold(g,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1])
def v_bgnorm_deskew(im): return pil(_deskew(bgnorm(to_gray(im))))
def v_green(im):
    a = np.array(im.convert("RGB")); return pil(bgnorm(a[:,:,1]))
def v_clean(im): return clean_for_ocr(im)

VARIANTS = dict(clean=v_clean, raw=v_raw, gray=v_gray, clahe=v_clahe, bgnorm=v_bgnorm,
                bgnorm_otsu=v_bgnorm_otsu, bgnorm_deskew=v_bgnorm_deskew, green_bgnorm=v_green)

pages = sys.argv[1].split(",")
names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(VARIANTS)
psm = int(sys.argv[3]) if len(sys.argv) > 3 else 6
for p in pages:
    truth = normalize((ROOT/"ground_truth"/f"1 ({p}).txt").read_text(encoding="utf-8"))
    img = Image.open(ROOT/"samples"/"skanime_300dpi"/f"1 ({p}).jpg")
    for n in names:
        t = time.time()
        r = ocr_image(VARIANTS[n](img), psm=psm)
        cer = edit_distance(list(truth), list(normalize(r.text))) / len(truth)
        print(f"1({p}) psm{psm} {n:<14} CER {cer:6.1%}  kept {r.kept_word_count}/{r.word_count}  conf {r.mean_confidence:.0f}  {time.time()-t:.0f}s", flush=True)
