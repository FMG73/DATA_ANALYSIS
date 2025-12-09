import requests
from pathlib import Path

def descargar_dashboard(server, site, token_name, token_value, view_name, output_path):

    # ---- Login ----
    auth = f"{server}/api/3.23/auth/signin"
    payload = {
        "credentials": {
            "personalAccessTokenName": token_name,
            "personalAccessTokenSecret": token_value,
            "site": {"contentUrl": site}
        }
    }
    r = requests.post(auth, json=payload)
    r.raise_for_status()
    token = r.json()["credentials"]["token"]
    site_id = r.json()["credentials"]["site"]["id"]
    headers = {"X-Tableau-Auth": token}

    # ---- Buscar directamente la view por nombre ----
    views_url = f"{server}/api/3.23/sites/{site_id}/views"
    r = requests.get(views_url, headers=headers)
    r.raise_for_status()

    views = r.json()["views"]["view"]
    view_id = next((v["id"] for v in views if v["name"].lower() == view_name.lower()), None)

    if not view_id:
        raise ValueError(f"No existe la vista: {view_name}")

    # ---- Descargar imagen ----
    img_url = f"{server}/api/3.23/sites/{site_id}/views/{view_id}/image"
    img = requests.get(img_url, headers=headers)
    img.raise_for_status()

    Path(output_path).write_bytes(img.content)

    # ---- Logout ----
    requests.post(f"{server}/api/3.23/auth/signout", headers=headers)

    return output_path