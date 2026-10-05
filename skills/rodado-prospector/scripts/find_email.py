#!/usr/bin/env python3
"""Find the contact emails a company publishes on its own website, and check the domain accepts mail.

Usage:
    python find_email.py <website or domain> [--extra URL ...]

Visits the home page plus the usual contact pages (contacto, contact, nosotros, about, ...) and any
--extra URLs (e.g. a Facebook "about" page or a press page you found). Collects emails from mailto:
links and visible text (including "name [at] domain [dot] com" forms), keeps only addresses on the
company's own domain (or explicitly listed public ones), ranks them, and checks the domain's MX records.

Prints JSON: {"domain", "mx": true/false, "emails": [{"email", "source", "kind", "score"}], "best"}
kind: marketing | named | general | sales | other.  Stdlib only.
"""
import html
import json
import re
import sys
import urllib.parse
import urllib.request

PATHS = ["", "contacto", "contactos", "contactanos", "contáctanos", "contact", "contact-us", "nosotros",
         "quienes-somos", "about", "about-us", "empresa", "prensa", "press", "trabaja-con-nosotros"]
UA = "Mozilla/5.0 (compatible; RodadoContactCheck/1.0; +https://roda.do)"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
AT = re.compile(r"\s*[\[\(\{]\s*(?:at|arroba|@)\s*[\]\)\}]\s*", re.I)
DOT = re.compile(r"\s*[\[\(\{]\s*(?:dot|punto|\.)\s*[\]\)\}]\s*", re.I)
SKIP = ("example.", "sentry", "wixpress", "@2x", ".png", ".jpg", ".webp", "domain.com", "email.com", "yourdomain")
RANK = [("marketing", ("mercadeo", "marketing", "mkt", "comunicacion", "comunicaciones", "marca", "brand", "publicidad", "prensa", "media")),
        ("general", ("info", "contacto", "contact", "hola", "hello", "servicio", "atencion", "clientes")),
        ("sales", ("ventas", "sales", "comercial", "pedidos"))]
SCORE = {"marketing": 3, "named": 3, "general": 2, "sales": 1, "other": 0}


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es,en"})
        with urllib.request.urlopen(req, timeout=15) as r:
            if "text/html" not in r.headers.get("Content-Type", "text/html"):
                return ""
            return r.read(800_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    except Exception:
        return ""


def mx(domain):
    try:
        u = "https://dns.google/resolve?" + urllib.parse.urlencode({"name": domain, "type": "MX"})
        with urllib.request.urlopen(u, timeout=10) as r:
            return bool(json.loads(r.read()).get("Answer"))
    except Exception:
        return None                      # unknown (network)


def kind(local):
    l = local.lower()
    for k, words in RANK:
        if any(w in l for w in words):
            return k
    if re.fullmatch(r"[a-z]+[._-]?[a-z]+", l) and not any(x in l for x in ("admin", "web", "noreply", "no-reply", "soporte", "support", "rrhh", "empleo", "facturacion", "billing")):
        return "named"                   # e.g. maria.perez@, mperez@
    return "other"


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    site = argv[1] if "://" in argv[1] else "https://" + argv[1]
    host = urllib.parse.urlparse(site).hostname.lower().removeprefix("www.")
    base = f"{urllib.parse.urlparse(site).scheme}://{urllib.parse.urlparse(site).netloc}/"
    extra = [argv[i + 1] for i, a in enumerate(argv) if a == "--extra"]
    found = {}
    for url in [urllib.parse.urljoin(base, p) for p in PATHS] + extra:
        page = fetch(url)
        if not page:
            continue
        text = html.unescape(page)
        cands = set(re.findall(r"mailto:([^\"'?>\s]+)", text, re.I)) | set(EMAIL.findall(text))
        cands |= set(EMAIL.findall(DOT.sub(".", AT.sub("@", text))))   # "name [at] marca [dot] com [dot] do"
        for e in cands:
            e = urllib.parse.unquote(e).strip().strip(".").lower()
            if not EMAIL.fullmatch(e) or any(s in e for s in SKIP):
                continue
            dom = e.split("@")[1]
            if not (dom == host or dom.endswith("." + host) or host.endswith(dom)) and url not in extra:
                continue                 # someone else's address (agency, web designer, plugin)
            found.setdefault(e, url)
    emails = []
    for e, src in found.items():
        k = kind(e.split("@")[0])
        emails.append({"email": e, "source": src, "kind": k, "score": SCORE[k]})
    emails.sort(key=lambda x: -x["score"])
    has_mx = mx(host)
    print(json.dumps({"domain": host, "mx": has_mx, "emails": emails,
                      "best": emails[0]["email"] if emails and has_mx is not False else None},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv)
