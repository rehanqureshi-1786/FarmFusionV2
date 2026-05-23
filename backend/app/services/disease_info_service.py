import json
import urllib.parse
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class DiseaseInfoService:
    WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    HEADERS = {
        "User-Agent": "FarmFusion/1.0 (https://farmfusion1.onrender.com)",
        "Accept": "application/json",
    }

    @staticmethod
    def _fetch_wikipedia_summary(disease_name: str) -> Optional[Dict[str, Any]]:
        title = urllib.parse.quote(disease_name.replace(" ", "_"))
        url = DiseaseInfoService.WIKIPEDIA_SUMMARY_URL.format(title=title)
        req = Request(url, headers=DiseaseInfoService.HEADERS)

        try:
            with urlopen(req, timeout=10) as response:
                data = json.load(response)
                if not isinstance(data, dict):
                    return None
                if data.get("type") in ["disambiguation", "https://mediawiki.org/wiki/HyperSwitch/errors/not_found"]:
                    return None

                return {
                    "title": data.get("title"),
                    "description": data.get("extract"),
                    "source_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
                }
        except HTTPError as exc:
            if exc.code == 404:
                return None
            raise RuntimeError(f"Wikipedia lookup failed ({exc.code}): {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"Wikipedia lookup failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError("Wikipedia returned invalid JSON") from exc

    @staticmethod
    def get_disease_info(disease_name: str) -> Dict[str, Any]:
        name = disease_name.strip()
        if not name or name.lower() in ["unknown", "healthy", "none"]:
            raise ValueError("No disease information available for unknown or healthy crops.")

        summary = DiseaseInfoService._fetch_wikipedia_summary(name)
        if summary:
            return {
                "name": summary["title"],
                "description": summary["description"],
                "source": summary["source_url"],
                "note": "This summary is sourced from Wikipedia and should be validated by a local agricultural expert.",
            }

        return {
            "name": name,
            "description": (
                f"Information for '{name}' was not found in Wikipedia."
                " Consult local agricultural extension services or an expert agronomist for accurate diagnosis and treatment."
            ),
            "source": None,
            "note": "No authoritative disease summary is available from the configured knowledge API.",
        }
