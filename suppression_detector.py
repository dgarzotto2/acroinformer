# suppression_detector.py

import fitz

def detect_suppression_flags(file_path):
    flags = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text = page.get_text()
            if "Preview" in text and len(text.strip()) < 10:
                flags.append("Visual placeholder detected: only 'Preview' text visible.")
            if page.rotation in [90, 180, 270]:
                flags.append(f"Page rotated {page.rotation} degrees – may indicate raster overlay.")

        for i in range(len(doc)):
            img_list = doc.get_page_images(i)
            if img_list and not doc[i].get_text().strip():
                flags.append(f"Page {i+1} is image-only – possible raster suppression.")

    except Exception as e:
        flags.append(f"Suppression check error: {e}")

    return flags