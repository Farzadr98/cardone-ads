from mongoengine import (
    connect,
    Document,
    StringField,
    GeoPointField,
    URLField
)

connect('AD')

class Advertisement(Document):
    title = StringField(max_length=100, required=True)
    location = GeoPointField(required=True)
    gif_url = URLField(required=False)  
    image_url = URLField(required=False)  
    video_url = URLField(required=False)  


    
