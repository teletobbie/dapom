from pathlib import Path
import chardet

def get_encoding_from_file(filepath):
    detected = chardet.detect(Path(filepath).read_bytes())
    return detected.get("encoding")