"""Image cleanup before OCR: grayscale, deskew, denoise, binarize.

Old typewritten archive scans tend to be skewed, low-contrast, and noisy
(paper texture, ink bleed). Cleaning this up before Tesseract sees it
measurably improves recognition quality.
"""
import cv2
import numpy as np
from PIL import Image


def _pil_to_cv(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def _cv_to_pil(mat: np.ndarray) -> Image.Image:
    return Image.fromarray(mat)


def _deskew(gray: np.ndarray) -> np.ndarray:
    binarized = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(binarized > 0))
    if coords.size == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    if abs(angle) < 0.1:
        return gray
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray, rotation_matrix, (w, h),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE,
    )


def clean_for_ocr(image: Image.Image) -> Image.Image:
    mat = _pil_to_cv(image)
    gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
    gray = _deskew(gray)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    binarized = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15,
    )
    return _cv_to_pil(binarized)
