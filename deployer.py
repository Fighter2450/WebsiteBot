import requests
import re


def deploy_to_gist(github_token: str, business_name: str, html: str) -> str:
    """Upload HTML to a public GitHub Gist and return a htmlpreview.github.io URL."""
    safe_name = re.sub(r"[^a-z0-9]+", "-", business_name.lower()).strip("-")
    filename = f"{safe_name}.html"

    response = requests.post(
        "https://api.github.com/gists",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json",
        },
        json={
            "description": f"Website preview for {business_name}",
            "public": True,
            "files": {filename: {"content": html}},
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    raw_url = data["files"][filename]["raw_url"]
    # htmlpreview renders raw GitHub content as a real webpage
    preview_url = f"https://htmlpreview.github.io/?{raw_url}"
    return preview_url
