import pytest
from app.tools.weather_tool import weather_tool, WeatherInput

from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_weather_tool_success():
    mock_payload = {
        "current": {"temperature_2m": 28.5, "wind_speed_10m": 12.0, "weather_code": 0},
        "daily": {
            "time": ["2026-08-27"],
            "temperature_2m_max": [34.0],
            "temperature_2m_min": [24.0],
            "precipitation_probability_max": [10.0],
            "weather_code": [0],
        }
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_payload
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        input_data = WeatherInput(latitude=26.9124, longitude=75.7873, location_name="Jaipur")
        output = await weather_tool(input_data)
        
        assert output.error is None
        assert output.location == "Jaipur"
        assert isinstance(output.temperature_c, float)
        assert len(output.daily_forecast) > 0
        assert output.condition != "Unavailable"

@pytest.mark.asyncio
async def test_weather_tool_fallback_on_error():
    # Invalid coordinates to trigger error handling
    input_data = WeatherInput(latitude=999.0, longitude=999.0, location_name="InvalidLoc")
    output = await weather_tool(input_data)
    
    assert output.error is not None
    assert output.condition == "Unavailable"
