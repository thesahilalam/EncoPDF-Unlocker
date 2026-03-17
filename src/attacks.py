import pikepdf
import itertools
import string

# Global for multiprocessing
_pdf_path = None

def init_worker(path):
    global _pdf_path
    _pdf_path = path

def check_password_worker(password):
    """Core function run by each CPU core."""
    try:
        with pikepdf.open(_pdf_path, password=password):
            return password
    except:
        return None

def brute_force_gen(charset_choice, min_l, max_l, skip=0):
    if charset_choice == "1": chars = string.digits
    elif charset_choice == "2": chars = string.ascii_letters
    else: chars = string.ascii_letters + string.digits + string.punctuation
    
    current_count = 0
    for length in range(min_l, max_l + 1):
        for combo in itertools.product(chars, repeat=length):
            if current_count < skip:
                current_count += 1
                continue
            yield "".join(combo)

def dictionary_gen(file_path, skip=0):
    current_count = 0
    with open(file_path, 'r', encoding='latin-1') as f:
        for line in f:
            if current_count < skip:
                current_count += 1
                continue
            yield line.strip()

def aadhaar_gen(name="", skip=0):
    years = range(1950, 2051)
    current_count = 0
    if name:
        prefix = name.upper()[:4]
        for y in years:
            if current_count < skip:
                current_count += 1
                continue
            yield f"{prefix}{y}"
    else:
        for combo in itertools.product(string.ascii_uppercase, repeat=4):
            prefix = "".join(combo)
            for y in years:
                if current_count < skip:
                    current_count += 1
                    continue
                yield f"{prefix}{y}"

def epan_gen(skip=0):
    current_count = 0
    for y in range(1950, 2051):
        for m in range(1, 13):
            days = 29 if m == 2 else (30 if m in [4,6,9,11] else 31)
            for d in range(1, days + 1):
                if current_count < skip:
                    current_count += 1
                    continue
                yield f"{d:02d}{m:02d}{y}"