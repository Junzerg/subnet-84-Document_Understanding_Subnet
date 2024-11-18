import os
import random
import json
from PIL import Image, ImageDraw, ImageFont
from math import floor
import requests
import base64
import io
import bittensor as bt

script_dir = os.path.dirname(os.path.abspath(__file__))

class GenerateCheckboxTextPair:
    def __init__(self, url, uid):
        self.url = url if url else "http://3.21.227.102:3000/api/tatsu/random-part-two"
        self.uid = uid
        
    def get_random_image_path(self, timeout=10):

        try:
            # Send a GET request to the API with timeout
            response = requests.get(self.url, timeout=timeout)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response JSON
                response_data = response.json()
                if response_data.get('status') is True:
                    # Access the 'data' section which contains image and labels
                    data = response_data.get('data')
                    if data:
                        image_url = data.get('image_url')
                        if image_url:
                            # Fetch the image (binary format) with timeout
                            image_response = requests.get(image_url, timeout=timeout)
                            if image_response.status_code == 200:
                                bt.logging.info(f"[{self.uid}] Image received successfully!")
                                image = image_response.content  # Image in binary format
                                # Open the binary data as a PIL Image
                                return Image.open(io.BytesIO(image)).convert("RGB")
                            bt.logging.info(f"[{self.uid}] Successfully retrieved image and label.")
                        else:
                            bt.logging.info(f"[{self.uid}] Error: Could not retrieve image URL or label data.")
                            return None
                    else:
                        bt.logging.info(f"[{self.uid}] Error: 'data' field is missing in the response.")
                        return None
                else:
                    bt.logging.info(f"[{self.uid}] Error: The request status is False.")
                    return None
            else:
                bt.logging.info(f"[{self.uid}] Failed to retrieve data. Status code: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            bt.logging;error(f"[{self.uid}] Request timed out after {timeout} seconds.")
            return None
        except requests.exceptions.RequestException as e:
            bt.logging;error(f"[{self.uid}] An error occurred: {e}")
            return None

    def is_window_empty(self, window, threshold=240, empty_percentage=0.9999):
        """Check if the window region is mostly empty (white)."""
        pixels = list(window.getdata())
        white_pixels = sum(1 for pixel in pixels if sum(pixel[:3]) > threshold * 3)
        return white_pixels >= empty_percentage * len(pixels)

    def find_empty_region(self, image, window_width, window_height, h_stride=15, v_stride=10):
        """Find an empty region in the image by moving a search window with defined strides."""
        width, height = image.size
        starting_points = [(0, 0), (50, 50), (100, 1000), (0, 500), (100, 500), (150, 500), (200, 500)]
        
        # Randomly select a starting point
        start_x, start_y = random.choice(starting_points)

        # Ensure starting point is within image bounds
        start_x = min(start_x, width - window_width)
        start_y = min(start_y, height - window_height)

        for y in range(start_y, height - window_height, v_stride):
            for x in range(start_x, width - window_width, h_stride):
                window = image.crop((x, y, x + window_width, y + window_height))
                if self.is_window_empty(window):
                    return x + 5, y + 5  # Add 5 pixels padding for checkbox and text
        return None, None  # No empty region found

    def get_random_metadata(self):
        text_color = random.choice([
            (70, 68, 66), (55, 58, 65), (72, 64, 60), (63, 55, 70),
            (67, 72, 62), (58, 66, 72), (75, 60, 65), (65, 58, 73),
            (68, 63, 57), (73, 70, 62)
        ])
        
        checkbox_text_size = random.choice([
            (20, 10), (22, 11), (24, 12), (26, 13), (28, 14), (30, 15)
        ])
        
        padding = random.choice([6, 7, 8, 9, 10])
        
        checkbox_stroke = random.choice([1, 2, 3])

        fonts = random.choice([
            ImageFont.truetype(os.path.join(script_dir, "fonts/Arial.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/Arial_Bold_Italic.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/Courier_New.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/DroidSans-Bold.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/FiraMono-Regular.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/Times New Roman.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/Vera.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/Verdana_Bold_Italic.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/Verdana.ttf"), checkbox_text_size[1]),
            ImageFont.truetype(os.path.join(script_dir, "fonts/DejaVuSansMono-Bold.ttf"), checkbox_text_size[1])
        ])
        
        return {
            "text_color": text_color,
            "checkbox_text_size": checkbox_text_size,
            "padding": padding,
            "checkbox_stroke": checkbox_stroke,
            "font": fonts
        }

    def draw_random_checkbox(self, draw, x, y, checkbox_size, checkbox_color):
        """
        Draws a random tick or cross with slight imperfections to simulate natural human checks.
        """
        # Randomly decide whether to draw a tick or a cross
        if random.choice([True, False]):  # Draw tick
            tick_variation = random.randint(1, 5)
            
            if tick_variation == 1:  # Basic tick
                draw.line((x, y + checkbox_size // 2, x + checkbox_size // 2, y + checkbox_size), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size // 2, y + checkbox_size, x + checkbox_size, y), fill=checkbox_color, width=2)
            
            elif tick_variation == 2:  # Slightly imperfect tick
                draw.line((x + random.randint(-2, 2), y + checkbox_size // 2, x + checkbox_size // 2 + random.randint(-2, 2), y + checkbox_size), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size // 2 + random.randint(-2, 2), y + checkbox_size, x + checkbox_size + random.randint(-2, 2), y), fill=checkbox_color, width=2)
            
            elif tick_variation == 3:  # Off-center tick
                draw.line((x + random.randint(0, 2), y + checkbox_size // 2, x + checkbox_size // 2 + 2, y + checkbox_size - 3), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size // 2, y + checkbox_size, x + checkbox_size - 2, y - 3), fill=checkbox_color, width=2)
            
            elif tick_variation == 4:  # Tilted tick
                draw.line((x, y + checkbox_size // 2, x + checkbox_size // 3, y + checkbox_size + 2), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size // 3, y + checkbox_size, x + checkbox_size, y - 1), fill=checkbox_color, width=2)
            
            elif tick_variation == 5:  # Tick going slightly out of the box
                draw.line((x - 1, y + checkbox_size // 2, x + checkbox_size // 2, y + checkbox_size + 2), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size // 2, y + checkbox_size + 1, x + checkbox_size + 2, y - 1), fill=checkbox_color, width=2)

        else:  # Draw cross
            cross_variation = random.randint(1, 5)
            
            if cross_variation == 1:  # Basic cross
                draw.line((x, y, x + checkbox_size, y + checkbox_size), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size, y, x, y + checkbox_size), fill=checkbox_color, width=2)
            
            elif cross_variation == 2:  # Slightly imperfect cross
                draw.line((x + random.randint(-2, 2), y, x + checkbox_size + random.randint(-2, 2), y + checkbox_size), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size + random.randint(-2, 2), y, x + random.randint(-2, 2), y + checkbox_size), fill=checkbox_color, width=2)
            
            elif cross_variation == 3:  # Cross tilted outward
                draw.line((x - 1, y - 1, x + checkbox_size + 1, y + checkbox_size + 1), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size + 1, y - 1, x - 1, y + checkbox_size + 1), fill=checkbox_color, width=2)
            
            elif cross_variation == 4:  # Cross slightly going out of the box
                draw.line((x - 1, y, x + checkbox_size + 2, y + checkbox_size), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size + 2, y - 1, x - 2, y + checkbox_size + 1), fill=checkbox_color, width=2)
            
            elif cross_variation == 5:  # Irregular cross with random shifts
                draw.line((x + random.randint(-2, 2), y + random.randint(-2, 2), x + checkbox_size + random.randint(-2, 2), y + checkbox_size + random.randint(-2, 2)), fill=checkbox_color, width=2)
                draw.line((x + checkbox_size + random.randint(-2, 2), y + random.randint(-2, 2), x + random.randint(-2, 2), y + checkbox_size + random.randint(-2, 2)), fill=checkbox_color, width=2)

    def put_text_randomly(self, draw, x, y, checkbox_size, text, font, text_color, width, height):
        """
        Draws the given text randomly at either the right or bottom of the checkbox.
        Ensures that the text fits within the image bounds.
        """
        # Randomly choose whether to place text to the right or at the bottom
        choice = random.choice(["right", "bottom"])

        padding = 10  # Space between checkbox and text

        if choice == "right":
            # Place text to the right of the checkbox
            text_x, text_y = x + checkbox_size + padding, y + 5
            text_width, text_height = draw.textsize(text, font=font)

            # Ensure text fits within image bounds
            if text_x + text_width > width:
                text_x = width - text_width - 1
            if text_y + text_height > height:
                text_y = height - text_height - 1

            draw.text((text_x, text_y), text, fill=text_color, font=font)

        elif choice == "bottom":
            # Place text below the checkbox
            text_x, text_y = x + checkbox_size // 2 - draw.textsize(text, font=font)[0] // 2, y + checkbox_size + padding
            text_width, text_height = draw.textsize(text, font=font)

            # Ensure text fits within image bounds
            if text_x + text_width > width:
                text_x = width - text_width - 1
            if text_y + text_height > height:
                text_y = height - text_height - 1

            draw.text((text_x, text_y), text, fill=text_color, font=font)
        return text_x, text_y, text_width, text_height

    def draw_checkbox_text_pairs(self):
        total_checkboxes_drawn = 0
        max_attempts = 50  # Limit the number of retries to prevent infinite loops
        
        while total_checkboxes_drawn == 0 and max_attempts > 0:
            # Fetch a random image
            image = self.get_random_image_path()
            metadata = self.get_random_metadata()
            font = metadata.get("font", ImageFont.load_default())
            number_of_pairs = random.choice([1, 2, 3])
            json_data = {"checkboxes": []}
            total_checkboxes_drawn = 0  # Reset count for this attempt

            if image:
                draw = ImageDraw.Draw(image)
                width, height = image.size

                # Define search window dimensions based on image size
                window_width = int(0.25 * width)
                window_height = floor(0.13 * height)
                
                for _ in range(number_of_pairs):
                    # Find an empty region in the image
                    x, y = self.find_empty_region(image, window_width, window_height)
                    if x is None or y is None:
                        bt.logging.info(f"No empty region found. Skipping.")
                        continue

                    # Define checkbox size and color
                    checkbox_size = metadata.get("checkbox_text_size", (20, 10))[0]
                    checkbox_color = metadata.get("text_color", (60, 60, 60))
                    text_color = metadata.get("text_color", (60, 60, 60))

                    text_options = [
                        "profit margin",
                        "clinical trial",
                    ]
                    with open(os.path.join(script_dir, "random_words.txt"), "r") as file:
                        text_options = [line.strip() for line in file]

                    text = random.choice(text_options)

                    # Draw checkbox
                    checkbox_coords = [x, y, x + checkbox_size, y + checkbox_size]
                    draw.rectangle(checkbox_coords, outline=checkbox_color, width=metadata.get("checkbox_stroke", 2))

                    # Draw tick or cross within the checkbox
                    self.draw_random_checkbox(draw, x, y, checkbox_size, checkbox_color)

                    text_x, text_y, text_width, text_height = self.put_text_randomly(draw, x, y, checkbox_size, text, font, text_color, width, height)

                    # Save annotation in JSON format
                    json_data["checkboxes"].append(
                        {
                            "checkbox_boundingBox": [x, y, x + checkbox_size, y, x + checkbox_size, y + checkbox_size, x, y + checkbox_size],
                            "boundingBox": [
                                text_x, text_y,
                                text_x + text_width, text_y,
                                text_x + text_width, text_y + text_height,
                                text_x, text_y + text_height
                            ],
                            "text": text
                        }
                    )
                    total_checkboxes_drawn += 1

                # If no checkboxes were drawn, retry
                if total_checkboxes_drawn == 0:
                    bt.logging.info(f"[{self.uid}] No synthetic image generate, retrying a new image.")
                    max_attempts -= 1
                    continue

                bt.logging.info(f"[{self.uid}] Synthetic image generated successfully")
                return json_data, image

        bt.logging.info(f"[{self.uid}] Failed to draw any checkboxes after multiple attempts.")
        return None, None



if __name__ == "__main__":
    checkbox_data_generator_object = GenerateCheckboxTextPair("", "")
    checkbox_data_generator_object.draw_checkbox_text_pairs()
