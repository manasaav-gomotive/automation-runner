import requests
import os

def get_token(config):
    token = os.getenv(config.auth_token_env)

    if not token:
        raise Exception(
            f"Missing API token.\n"
            f"Set it using:\nexport {config.auth_token_env}=<token>"
        )

    print("[AUTH] Token loaded ✓")
    return token

def fetch_tokens(base_url, email, password):
    url = f"{base_url}/api/fa1/sessions"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "user": {
                "email": email,
                "password": password
            }
        },
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"Login failed: {response.text}")

    data = response.json()["user"]

    return {
        "AUTH_TOKEN": data["authentication_token"],
        "WEB_TOKEN": data["web_auth_token"]
    }