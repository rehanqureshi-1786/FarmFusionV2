import pytest
from app.tools.weather_tool import weather_tool, WeatherInput

@pytest.mark.asyncio
async def test_weather_tool_success():
    # Jaipur coordinates
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
