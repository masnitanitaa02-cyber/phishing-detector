import re
import math
from urllib.parse import urlparse

MULTI_LEVEL_TLD = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "co.id", "co.jp", "or.jp",
    "ac.jp", "ne.jp", "com.au", "edu.au", "org.au", "gov.au", "net.au",
    "co.nz", "org.nz", "co.za", "com.br", "co.in", "com.sg", "co.kr",
    "gov.br", "edu.br", "org.br", "net.br", "rj.gov.br", "sp.gov.br",
    "gov.it", "edu.it", "ac.in", "gov.in", "co.th", "ac.th", "go.jp",
    "gov.cn", "edu.cn", "com.cn", "co.il", "ac.il", "gov.il",
    "or.kr", "go.kr", "ac.kr", "ne.kr",
    "lg.jp", "ed.jp",
}

# 22 fitur yang digunkan 
FEATURE_COLS = [
    "url_len", "dom_len", "is_ip", "tld_len", "subdom_cnt",
    "letter_cnt", "digit_cnt", "special_cnt", "eq_cnt", "qm_cnt",
    "amp_cnt", "dot_cnt", "dash_cnt", "under_cnt", "letter_ratio",
    "digit_ratio", "spec_ratio", "is_https", "slash_cnt", "entropy",
    "path_len", "query_len"
]


def _shannon_entropy(s: str) -> float:
    """Hitung entropy Shannon dari string (per karakter)."""
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(s)
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def _is_ip_address(host: str) -> int:
    """Cek apakah host berupa alamat IP (bukan domain biasa)."""
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    return 1 if re.match(pattern, host) else 0


def _get_domain_and_tld(host: str):
    """
    Pisahkan host jadi (domain_utama, tld, jumlah_subdomain).
    Aturan: 2 label terakhir = domain utama + tld (misal 'rmit.edu.au' -> tld 'au'
    secara default), KECUALI 2/3 label terakhir cocok dengan TLD multi-level
    (misal 'edu.au', 'gov.br') maka domain utama = label sebelum TLD multi-level itu.
    Subdomain count dihitung dari total label host (termasuk www) dikurangi
    label domain utama dan label TLD.
    """
    parts = host.split(".")
    if len(parts) < 2:
        return host, "", 0

    # Cek TLD 3-level dulu (misal rj.gov.br), baru 2-level (edu.au), baru 1-level (com)
    tld = parts[-1]
    if len(parts) >= 4:
        last_three = ".".join(parts[-3:])
        if last_three in MULTI_LEVEL_TLD:
            tld = last_three
    if tld == parts[-1] and len(parts) >= 3:
        last_two = ".".join(parts[-2:])
        if last_two in MULTI_LEVEL_TLD:
            tld = last_two

    tld_label_count = len(tld.split("."))
    domain_label_count = 1  # nama domain utama, misal "rmit" / "cnr"

    # dom = domain_label + tld (tanpa subdomain di depan), misal "rmit.edu.au" atau "cnr.it"
    dom_parts = parts[-(domain_label_count + tld_label_count):]
    dom = ".".join(dom_parts)

    subdom_cnt = len(parts) - (domain_label_count + tld_label_count)
    subdom_cnt = max(subdom_cnt, 0)

    return dom, tld, subdom_cnt


def extract_features(url: str) -> dict:
    """
    Extract 22 fitur dari URL mentah. Return dict siap dipakai sebagai
    1 baris dataframe, urutan kolom sesuai FEATURE_COLS.
    """
    url = url.strip()
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url  # fallback kalau user lupa nulis scheme

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path or ""
    query = parsed.query or ""

    # Buang port kalau ada (misal host:8080)
    host_no_port = host.split(":")[0]

    is_ip = _is_ip_address(host_no_port)
    dom, tld, subdom_cnt = _get_domain_and_tld(host_no_port)

    url_len = len(url)
    dom_len = len(dom)
    tld_len = len(tld)
    path_len = len(path)
    query_len = len(query)

    letter_cnt = sum(c.isalpha() for c in url)
    digit_cnt = sum(c.isdigit() for c in url)
    # special_cnt = semua karakter NON-alfanumerik (titik, slash, colon, dash, dll)
    special_cnt = sum(not c.isalnum() for c in url)

    eq_cnt = url.count("=")
    qm_cnt = url.count("?")
    amp_cnt = url.count("&")
    dot_cnt = url.count(".")
    dash_cnt = url.count("-")
    under_cnt = url.count("_")
    slash_cnt = url.count("/")

    letter_ratio = letter_cnt / url_len if url_len else 0.0
    digit_ratio = digit_cnt / url_len if url_len else 0.0
    spec_ratio = special_cnt / url_len if url_len else 0.0

    is_https = 1 if parsed.scheme.lower() == "https" else 0
    entropy = _shannon_entropy(url)

    features = {
        "url_len": url_len,
        "dom_len": dom_len,
        "is_ip": is_ip,
        "tld_len": tld_len,
        "subdom_cnt": subdom_cnt,
        "letter_cnt": letter_cnt,
        "digit_cnt": digit_cnt,
        "special_cnt": special_cnt,
        "eq_cnt": eq_cnt,
        "qm_cnt": qm_cnt,
        "amp_cnt": amp_cnt,
        "dot_cnt": dot_cnt,
        "dash_cnt": dash_cnt,
        "under_cnt": under_cnt,
        "letter_ratio": letter_ratio,
        "digit_ratio": digit_ratio,
        "spec_ratio": spec_ratio,
        "is_https": is_https,
        "slash_cnt": slash_cnt,
        "entropy": entropy,
        "path_len": path_len,
        "query_len": query_len,
    }
    return features


if __name__ == "__main__":
    # Quick test manual
    test_urls = [
        "https://www.rmit.edu.au/",
        "http://www.latrobe.edu.au/",
        "https://www.dropbox.com/scl/fi/ukrohcguhc9anduhlaumg/We-urge-you-to-verify",
    ]
    for u in test_urls:
        feats = extract_features(u)
        print(u)
        print(feats)
        print()
