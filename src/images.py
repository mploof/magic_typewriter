from PIL import Image
import base64

from settings import config
import os

def resize_image(input_image_path, output_image_path, new_width):
    with Image.open(input_image_path) as img:
        original_width, original_height = img.size
        if original_width <= new_width:
            return
        aspect_ratio = original_height / original_width
        new_height = int(new_width * aspect_ratio)
        resized_img = img.resize((new_width, new_height))
        resized_img.save(output_image_path)
        print(f"The image has been resized to {new_width}x{new_height}")

def get_base64_image_url(image_name):
    image_path = os.path.join(config["images_dir"], image_name)
    resize_image(image_path, image_path, 1024)
    with open(image_path, "rb") as image_file:
        base64_image =  base64.b64encode(image_file.read()).decode('utf-8')
        url = f"data:image/jpeg;base64,{base64_image}"
        return url