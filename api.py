from __future__ import annotations

from typing import Optional, Any
from requests import Session, Timeout, RequestException, HTTPError
from dataclasses import dataclass
from pathlib import Path

from utils import get_env, haversine_km, norm_str, atomic_write_json
from errors import OpenSkyDeprecated, OpenSkyError, AdsdbError


DATA_PATH = Path("/var/lib/flighttracker/best_flight.json")

def construct_params() -> dict[str, float]:
    try:
        latitude = float(get_env("LATITUDE"))
        longitude = float(get_env("LONGITUDE"))
        delta = float(get_env("DIFF"))
        return {
            "lamin": latitude - delta,
            "lamax": latitude + delta,
            "lomin": longitude - delta,
            "lomax": longitude + delta,
        }
    except ValueError as e:
        raise RuntimeError("Got a runtime error: ", e) from e

def get_plane_states(session: Session) -> list[list[Any]]:
    try:
        url = "https://opensky-network.org/api/states/all"
        r = session.get(url, params=construct_params(),
                        timeout=(3.05, 10))
        
        if r.headers.get("Sunset") or r.headers.get("Deprecation"):
            raise OpenSkyDeprecated(
                f"OpenSky endpoint indicates deprecation: {url}"
                f"(Sunset={r.headers.get('Sunset')}, Deprecation={r.headers.get('Deprecation')})"
            )
        try:
            r.raise_for_status()
        except HTTPError as e:
            status = r.status_code
            if status in (404, 410):
                raise OpenSkyDeprecated(f"OpenSky endpoint not available (HTTP {status}): {url}") from e

            elif status in (401, 403):
                raise OpenSkyError(f"OpenSky auth/permission error (HTTP {status}).") from e
            
            snippet = (r.text or "").replace("\n", " ")
            raise OpenSkyError(f"OpenSky request failed (HTTP {status}). Body: {snippet}") from e
        
        content = r.json().get("states", [])
        
        # basic data validation
        if len(content) < 7:
            raise OpenSkyError("API result has changed, please consult the documentation.")
        
        return content
    
    except Timeout as e:
        raise OpenSkyError(f"Timed out calling OpenSky: {url}") from e
    
    except ValueError as e:
        raise OpenSkyError(f"Invalid JSON change from OpenSky: {url}") from e
    
    except RequestException as e:
        raise OpenSkyError(f"Network/requests error: {url}") from e
        
        
# I can't be bothered making a customized runtime error again :)
def find_adsbdb(session: Session, callsign: str) -> Optional[dict[str, Any]]:
    url = f"https://api.adsbdb.com/v0/callsign/{callsign}"
    try:
        r = session.get(url, timeout=(3.05, 10))
        try:
            r.raise_for_status()
        except HTTPError as e:
            status = r.status_code
            if status in (404, 410):
                return None

            elif status in (401, 403):
                raise AdsdbError(f"ADS-db auth/permission error (HTTP {status}).") from e
            
            snippet = (r.text or "").replace("\n", " ")
            raise AdsdbError(f"ADS-db request failed (HTTP {status}). Body: {snippet}") from e
        
        return r.json()

    except Timeout as e:
        raise RuntimeError(f"Timeed out calling the url: {url}") from e
    except ValueError as e:
        raise OpenSkyError(f"Invalid JSON change from OpenSky: {url}") from e
    except RequestException as e:
        raise OpenSkyError(f"Network/requests error: {url}") from e

def parse_route(route: dict[str, Any]) -> Optional[tuple, str, str]:
    fr = route.get("response" or {}).get("flightroute")
    origin = fr.get("origin" or {}).get("icao_code")
    dest = fr.get("destination" or {}).get("icao_code")
    if not origin or not dest:
        return None
    return str(origin), str(dest)

@dataclass
class BestFlight:
    flightcode: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    dist_km: Optional[str] = None

def get_closest_flight() -> Optional[BestFlight]:
    try:
        with Session() as s:
            home_lat, home_lon = float(get_env("LATITUDE")), float(get_env("LONGITUDE"))
            
            states = get_plane_states(s)
            
            # Build candidates, the list of tuple (distance, callsign).
            candidates = []
            for row in states:
                callsign, plane_lon, plane_lat = norm_str(row[1]), row[5], row[6]
                if (not callsign or 
                    not isinstance(plane_lat, (int, float)) or
                    not isinstance(plane_lon, (int, float))):
                    continue
                d = haversine_km(home_lat, home_lon, 
                                float(plane_lat), float(plane_lon))
                candidates.append((d, callsign))
            
            if not candidates:
                return None
            
            candidates.sort(key=lambda x: x[0])
            
            seen = set()
            for d, callsign in candidates:
                if callsign in seen:
                    continue
                seen.add(callsign)
                # Find ocode and dcode
                content = find_adsbdb(s, callsign)
                if content is None:
                    continue
                route = parse_route(content)
                if route:
                    ocode, decode = route
                    return BestFlight(
                        flightcode=callsign,
                        origin=ocode,
                        destination=decode,
                        dist_km=d
                    )
        return BestFlight(
            flightcode=candidates[0][1]
        )
    except ValueError as e:
        raise RuntimeError(f"Value error occured: {e}") 

if __name__ == "__main__":
    flight = get_closest_flight()
    if not flight:
        payload = {"source": "none", "flightcode": None}
    else:
        payload = {
            "flightcode": flight.flightcode,
            "origin": flight.origin,
            "destination": flight.destination,
            "dist_km": flight.dist_km,
        }
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(DATA_PATH, payload)
