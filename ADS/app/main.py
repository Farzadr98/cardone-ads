
# TODO:
# make urls for ad.py required
# note: returning mongodb objects as response creates maximum recrussion depth error
# error handling for funcs


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
        city: Annotated[Optional[str], Query(
            min_length=3,
            max_length=50,
            pattern="^[A-Za-z\s]+$"
        )] = None,
        long: Annotated[Optional[Decimal], Query()] = None,
        lat: Annotated[Optional[Decimal], Query()] = None
    ):

    if long and lat:
        try:
            lat = float(lat)
            long = float(long)
            point = [long, lat]
            print("point here:", point)
            return await get_near_points(point)
        except ValueError as ve:
            return {"status": "error", "message": f"Invalid latitude or longitude: {ve}"}

    if ip:
        point = await get_location_from_ip(ip)
        return await get_near_points(point)

    return {"status": "error", "message": "At least an ip address or longtitude and latitude are required."}

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
        return {"status": "error", "message": "Error fetching nearby points."}


async def get_location_from_ip(ip_address):
    try:
        url = f"http://ipwho.is/{ip_address}"
        response = await send_get_request(url)
        if 'error' in response:
            return {"error": response['error']}
        return [response.get('longitude'), response.get('latitude')]
    
    except Exception as e:
        logging.error(f"Error fetching location from IP: {e}")
        return {"error": str(e)}


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


