from typing import Optional

from app.agents.groq_client import GroqClient


class MarketAnalysisAgent:
    def predict(self, commodity: str, region: Optional[str]) -> float:
        prompt = (
            "You are an agricultural market analyst. Provide a predicted market price per kilogram "
            f"for {commodity} in {region or 'India'} over the next 30 days. "
            "Respond with a single numeric value only, in Indian rupees per kilogram."
        )
        client = GroqClient()
        raw = client.complete(prompt)
        try:
            return float(raw.strip().split()[0].replace(',', ''))
        except Exception as err:
            raise RuntimeError(f"Unable to parse market prediction response: {raw}") from err
