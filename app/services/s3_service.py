from ..config import config
import os


# S3 Settings
LIARA_ENDPOINT    = os.getenv("LIARA_ENDPOINT")
LIARA_BUCKET_NAME = os.getenv("LIARA_BUCKET_NAME")
LIARA_ACCESS_KEY  = os.getenv("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY  = os.getenv("LIARA_SECRET_KEY")


# set Liara Bucket Conf
LIARA = {
    'endpoint': s.LIARA_ENDPOINT,
    'accesskey': s.LIARA_ACCESS_KEY,
    'secretkey': s.LIARA_SECRET_KEY,
    'bucket': s.LIARA_BUCKET_NAME
}

