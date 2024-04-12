from PIL import Image

def resize_image(input_image_path, output_image_path, new_width):
    with Image.open(input_image_path) as img:
        original_width, original_height = img.size
        if original_width <= new_width:
            return
        aspect_ratio = original_height / original_width
        new_height = int(new_width * aspect_ratio)
        resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)
        resized_img.save(output_image_path)
        print(f"The image has been resized to {new_width}x{new_height}")

# Example usage:
input_image_path = './data/image.png'
output_image_path = './data/image.png'
new_width = 800  # You can change this to your desired width

resize_image(input_image_path, output_image_path, new_width)
