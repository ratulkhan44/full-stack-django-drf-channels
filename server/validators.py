# Python Imports
import os

# Third Party Imports
from PIL import Image

# In Django Imports
from django.core.exceptions import ValidationError


def validate_image_icon_size(image):
    if image:
        with Image.open(image) as img:
            if img.width > 70 and img.height > 70:
                raise ValidationError(
                    f"The maximaum allowed dimension for the image are 70x70 -size you are provided {img.size}"
                )
            

def validate_image_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extension = ['.jpg','.jpeg','.svg','.png','.gif']
    if ext not in valid_extension:
        raise ValidationError("Unsupported File Extension")