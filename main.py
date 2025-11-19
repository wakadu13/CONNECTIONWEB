import requests
import urllib3
from urllib.parse import urlparse, parse_qs

# Ne pas hurler sur le certificat du portail
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1) URL du portail telle que tu la vois dans ton navigateur
#    (page où tu tapes ton login/mot de passe)
PORTAL_PAGE_URL = "https://controller.access.network/portal/index.php?controllerHostname=controller.access.network"

LOGIN = "user"
PASSWORD = "password"  # à changer ici si besoin

def detect_controller(url: str) -> str:
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # 1) si ?controllerHostname=... existe, on le prend
    if "controllerHostname" in qs and qs["controllerHostname"]:
        host = qs["controllerHostname"][0]
    else:
        # 2) sinon, on prend l'hôte de l'URL
        host = parsed.hostname or ""

    # nettoyage de précaution
    host = host.replace("https://", "").replace("http://", "")
    host = host.split("/")[0]

    return host

controller = detect_controller(PORTAL_PAGE_URL)
PORTAL_API_URL = f"https://{controller}/portal_api.php"

# 2) En-têtes qui imitent un vrai navigateur
parsed = urlparse(PORTAL_PAGE_URL)
origin = f"{parsed.scheme}://{parsed.netloc}"

BROWSER_HEADERS = {
    # copie un User-Agent de ton vrai navigateur si tu veux être 100% fidèle
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": origin,
    "Referer": PORTAL_PAGE_URL,
    "X-Requested-With": "XMLHttpRequest",
}

# 3) Session pour garder les cookies comme un navigateur
session = requests.Session()

print("[+] GET portail (pour récupérer les cookies de session)…")
resp_get = session.get(PORTAL_PAGE_URL, headers=BROWSER_HEADERS, verify=False)
print("    Code HTTP GET portail :", resp_get.status_code)

# 4) Payload d'authentification : identique à ta requête brute
payload = {
    "action": "authenticate",
    "login": LOGIN,
    "password": PASSWORD,
    "policy_accept": "true",
    "from_ajax": "true",
    "wispr_mode": "false",
}

print("[+] POST authenticate vers", PORTAL_API_URL, "…")
resp_post = session.post(
    PORTAL_API_URL,
    headers=BROWSER_HEADERS,
    data=payload,
    verify=False,
)

print("    Code HTTP POST :", resp_post.status_code)
print("    Contenu (1000 premiers caractères) :")
print(resp_post.text[:1000])
