from mongoengine import (
    connect,
    Document,
    StringField,
    GeoPointField,
    URLField
)
from ..config import config
import os

username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')

connect('AD', username=username, password=password, authentication_source='admin')

class Advertisement(Document):
    title = StringField(max_length=100, required=True)
    location = GeoPointField(required=True)
    gif_url = URLField(required=False)  
    image_url = URLField(required=False)  
    video_url = URLField(required=False)  


    
