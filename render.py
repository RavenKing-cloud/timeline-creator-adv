# Install PILLOW library for image rendering
import subprocess;print(subprocess.Popen("pip install --upgrade PILLOW",shell=True,stdout=subprocess.PIPE).stdout.read())
# Imports
import PIL.Image,PIL.ImageDraw,PIL.ImageFont,json,numpy as np
# Json from the timeline json file
json=json.load(open('timeline.json'))
# Turn a date into a number ie; 6/26/24 as [6,26,24] would result in 17199
def datenum(date:list):
    return int(np.floor((date[0]/12+date[1]/365+date[2])*700))
# Set beginning and end of the timeline
start_date=datenum([json['start_date'][0]-4,json['start_date'][1],json['start_date'][2]])
end_date=datenum([json['end_date'][0]+4,json['end_date'][1],json['end_date'][2]])
# Length of the timeline
timeline_length=end_date-start_date
# Create the base image for the timeline
img=PIL.Image.new(mode="RGB",size=(timeline_length,720),color=(255,255,255)) # Background
draw=PIL.ImageDraw.Draw(img)
draw.line([(0,360),(timeline_length,360)],fill=(0,0,0),width=4) # Middle line
# Font for the text on the timeline
font=PIL.ImageFont.truetype('font.ttf',16)
# Show events on the timeline
event_num=0
for event in json['events']:
    event_num+=1
    # Setup event
    pos=datenum(event['date'])-start_date # Get events position on the timeline
    name=event['name'] # Get name of event
    # Prepare for text rendering
    text_img=PIL.Image.new('RGBA',(400,200),(255,255,255,0))  # Adjusted size for better accommodation of rotated text
    text_draw=PIL.ImageDraw.Draw(text_img)
    text_size=text_draw.textbbox((0,0),name,font=font)
    text_draw.text((0,0),name,(0,0,0),font=font)
    if (event_num % 2 == 1):
        draw.line([(pos,360),(pos,340),(pos+20,320)],fill=(0,0,0),width=4)
        # Rotate the text image by 45 degrees
        rotated_text_img=text_img.rotate(45,expand=True)
        # Calculate the correct position for the rotated text image
        x=pos+232-rotated_text_img.width//2
        y=244-rotated_text_img.height//2
    else:
        draw.line([(pos,360),(pos,380),(pos+20,400)],fill=(0,0,0),width=4)
        # Rotate the text image by -45 degrees
        rotated_text_img=text_img.rotate(-45,expand=True)
        # Calculate the correct position for the rotated text image
        x=pos+97-rotated_text_img.width//2
        y=612-rotated_text_img.height//2
    img.paste(rotated_text_img,(x,y),rotated_text_img)
# Loop through all the years the timeline covers
for i in range(json['end_date'][2]-json['start_date'][2]+1):
    pos=datenum([1,1,json['start_date'][2]+i])-start_date # Get position of the year
    draw.line([(pos,340),(pos,380)],fill=(0,0,0),width=4) # Draw line going through the main line
    draw.text((pos-19,326),str(json['start_date'][2]+i),(0,0,0),font=font) # Render text with the number of the year
# Top right text
font=PIL.ImageFont.truetype('font.ttf',36)
draw.text((10,10),json['timeline_name'],(0,0,0),font=font,align='left',anchor='lt')
# Save the image
img.save(r'timeline.png')
# Show the image in default image editor (Debugging)
img.show()

