import sys
import os
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Function to load JSON from a given file path
def load_json(file_path):
    with open(file_path) as f:
        return json.load(f)

# Function to convert a date into a numerical representation
def datenum(date: list):
    return int(np.floor((date[0] / 12 + date[1] / 365 + date[2]) * 700))

# Function to render the timeline image
def render_timeline(json_file_path):
    # Load JSON data from the specified file path
    timeline_data = load_json(json_file_path)

    # Set the beginning and end of the timeline
    start_date = datenum([timeline_data['start_date'][0] - 4, timeline_data['start_date'][1], timeline_data['start_date'][2]])
    end_date = datenum([timeline_data['end_date'][0] + 4, timeline_data['end_date'][1], timeline_data['end_date'][2]])

    # Calculate the length of the timeline
    timeline_length = end_date - start_date

    # Create the base image for the timeline
    img = Image.new(mode="RGB", size=(timeline_length, 720), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line([(0, 360), (timeline_length, 360)], fill=(0, 0, 0), width=4)  # Middle line

    # Use a relative path to the font file
    font_path = os.path.join(os.path.dirname(__file__), '..', 'font', 'font.ttf')
    font = ImageFont.truetype(font_path, 16)

    # Show events on the timeline
    event_num = 0
    for event in timeline_data['events']:
        event_num += 1
        pos = datenum(event['date']) - start_date  # Get event's position on the timeline
        name = event['name']  # Get name of the event

        # Prepare for text rendering
        text_img = Image.new('RGBA', (400, 200), (255, 255, 255, 0))  # Adjusted size for better accommodation of rotated text
        text_draw = ImageDraw.Draw(text_img)
        text_size = text_draw.textbbox((0, 0), name, font=font)
        text_draw.text((0, 0), name, (0, 0, 0), font=font)

        if event_num % 2 == 1:
            draw.line([(pos, 360), (pos, 340), (pos + 20, 320)], fill=(0, 0, 0), width=4)
            rotated_text_img = text_img.rotate(45, expand=True)
            x = pos + 232 - rotated_text_img.width // 2
            y = 244 - rotated_text_img.height // 2
        else:
            draw.line([(pos, 360), (pos, 380), (pos + 20, 400)], fill=(0, 0, 0), width=4)
            rotated_text_img = text_img.rotate(-45, expand=True)
            x = pos + 97 - rotated_text_img.width // 2
            y = 612 - rotated_text_img.height // 2

        img.paste(rotated_text_img, (x, y), rotated_text_img)

    # Loop through all the years the timeline covers
    for i in range(timeline_data['end_date'][2] - timeline_data['start_date'][2] + 1):
        pos = datenum([1, 1, timeline_data['start_date'][2] + i]) - start_date  # Get position of the year
        draw.line([(pos, 340), (pos, 380)], fill=(0, 0, 0), width=4)  # Draw line through the main line
        draw.text((pos - 19, 326), str(timeline_data['start_date'][2] + i), (0, 0, 0), font=font)  # Render year

    # Loop through all the months the timeline covers
    for i in range((timeline_data['end_date'][2] - timeline_data['start_date'][2] + 1)*12):
        pos = datenum([1, 1, timeline_data['start_date'][2] // 12 + i]) - start_date  # Get position of the month
        draw.line([(pos, 330), (pos, 370)], fill=(0, 0, 0), width=4)  # Draw line through the main line

    # Draw the top right text
    font_large = ImageFont.truetype(font_path, 36)
    draw.text((10, 10), timeline_data['timeline_name'], (0, 0, 0), font=font_large, align='left', anchor='lt')

    # Save the image with the same name as the JSON file
    json_file_name = os.path.basename(json_file_path)
    base_name = os.path.splitext(json_file_name)[0]
    img_path = os.path.join(os.path.dirname(__file__), '..', 'export', f'{base_name}.png')
    img.save(img_path)

    # Return the path to the saved image
    return img_path