"""Weather MCP server backed by Open-Meteo (free, no API key).

Run:  uv run server.py        (stdio transport, for Claude Desktop / Claude Code)
Test: uv run mcp dev server.py   (opens the MCP Inspector)
"""

import logging
import sys

import httpx
from mcp.server.fastmcp import FastMCP

# IMPORTANT: with stdio transport, stdout is the protocol channel.
# Log to stderr only, never print().
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("weather-mcp")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Separate connect/read timeouts: fail fast if unreachable, allow a bit longer to read.
TIMEOUT = httpx.Timeout(10.0, connect=5.0)

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Light showers", 81: "Showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
}

mcp = FastMCP("weather")


async def _get_json(url: str, params: dict) -> dict:
    """GET a URL and return JSON, converting httpx errors into clear messages.

    Exceptions raised inside a tool are caught by FastMCP and returned to the
    model as an error result (isError=True), so the model can explain or retry.
    """
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        raise RuntimeError("The weather service timed out. Try again in a moment.")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Weather service returned HTTP {e.response.status_code}.")
    except httpx.RequestError as e:
        raise RuntimeError(f"Could not reach the weather service: {type(e).__name__}.")
    except ValueError:
        raise RuntimeError("Weather service returned an invalid response.")


async def _geocode(city: str) -> dict:
    data = await _get_json(GEOCODING_URL, {"name": city, "count": 1, "language": "en"})
    results = data.get("results")
    if not results:
        raise ValueError(f"No location found for '{city}'. Try a more specific name.")
    return results[0]


def _place_name(loc: dict) -> str:
    parts = [loc.get("name"), loc.get("admin1"), loc.get("country")]
    return ", ".join(p for p in parts if p)


@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: City name, e.g. "Gurugram" or "Paris".
    """
    loc = await _geocode(city)
    data = await _get_json(FORECAST_URL, {
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                   "wind_speed_10m,weather_code",
        "timezone": "auto",
    })
    c = data["current"]
    u = data["current_units"]
    return (
        f"Current weather in {_place_name(loc)}:\n"
        f"- Conditions: {WEATHER_CODES.get(c['weather_code'], 'Unknown')}\n"
        f"- Temperature: {c['temperature_2m']}{u['temperature_2m']} "
        f"(feels like {c['apparent_temperature']}{u['apparent_temperature']})\n"
        f"- Humidity: {c['relative_humidity_2m']}{u['relative_humidity_2m']}\n"
        f"- Wind: {c['wind_speed_10m']} {u['wind_speed_10m']}"
    )


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get a daily weather forecast for a city.

    Args:
        city: City name, e.g. "Tokyo".
        days: Number of days to forecast (1-7).
    """
    if not 1 <= days <= 7:
        raise ValueError("days must be between 1 and 7.")

    loc = await _geocode(city)
    data = await _get_json(FORECAST_URL, {
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": days,
        "timezone": "auto",
    })
    d = data["daily"]
    u = data["daily_units"]
    lines = [f"{days}-day forecast for {_place_name(loc)}:"]
    for i, date in enumerate(d["time"]):
        lines.append(
            f"- {date}: {WEATHER_CODES.get(d['weather_code'][i], 'Unknown')}, "
            f"{d['temperature_2m_min'][i]}-{d['temperature_2m_max'][i]}{u['temperature_2m_max']}, "
            f"precip {d['precipitation_sum'][i]}{u['precipitation_sum']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")