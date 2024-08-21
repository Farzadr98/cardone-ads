
# TODO:
# a precise ip to location service is required
# make urls for ad.py required
# note: returning mongodb objects as response creates maximum recrussion depth error
# rate limiter
# remove exceptions from return

from decimal import Decimal
from typing import Annotated, Optional
from fastapi import FastAPI, Query
from .models.ad import Advertisement
from ip2geotools.databases.noncommercial import DbIpCity
import httpx
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.get("/")
async def root(
        ip: Annotated[Optional[str], Query(
            min_length=7,
            max_length=15,
            pattern="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )] = None,
        long: Annotated[Optional[Decimal], Query()] = None,
        lat: Annotated[Optional[Decimal], Query()] = None
    ):

    if long and lat:
        try:
            lat = float(lat)
            long = float(long)

            point = [long, lat]

            return await get_near_points(point)

        except ValueError as ve:
            return {"status": "error", "message": f"Invalid latitude or longitude: {ve}"}
        except Exception:
            return {"status": "error", "message": "error fethcing locations using geopoint"}

    if ip:

        point_response = await get_location_from_ip(ip)
        if "error" in point_response:
            return {"status": "error", "message": point_response.get("error")}
        elif "non-local" in point_response:
            message = point_response.get("non-local")
            return {"status": "success", "message": f"{message}, recommending best ads" }

        try:
            for geo in point_response:
                geo = float(geo)

            return await get_near_points(point_response)

        except ValueError as ve:
            return {"status": "error", "message": f"Invalid latitude or longitude: {ve}"}
        except Exception as e:
            return {"status": "error", "message": "error fethcing locations using geopoint"}

        return {"status": "success", "message": "no country detected, recommending best ads" }

    return {"status": "success", "message": "nothing to look up on, recommending best ads" }
    



async def get_near_points(point):


    try:
        objects = Advertisement.objects(location__near=point)
        
        if objects and len(objects) > 1:
            result_list = [obj.title for obj in objects]
            return {"status": "success", "ads": result_list}
        else:
            return {"status": "error", "message": "No nearby points found."}
    
    except Exception as e:
        logging.error(f"Error fetching nearby points: {e}")
        return {"status": "error", "message": f"Error fetching nearby points: {e}"}


async def get_location_from_ip(ip_address):

    # res types: error, non-local, lat and long

    try:
        url = f"http://ipwho.is/{ip_address}"
        response = await send_get_request(url)
        
        if response.get('error'):
            return {"error": response['error']}
        
        elif 'country' in response and response.get('country').strip().lower() != "iran":
            return {"non-local": "country outside range"}

        elif ('latitude' in response) and ('longitude' in response):
            return [response.get('longitude'), response.get('latitude')]

        else:
            return {"non-local": "no country detected"}
        
    
    except Exception as e:
        logging.error(f"Error fetching location from IP: {e}")
        return {"error": "error fetching location via IP adress"}



async def send_get_request(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return {"error": "Invalid JSON response"}
    
    except httpx.RequestError as e:
        logging.error(f"Request error: {e}")
        return {"error": str(e)}
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP status error: {e}")
        return {"error": str(e)}





