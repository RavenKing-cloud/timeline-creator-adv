# Timeline Creator

Made by TauCommands & RavenKing

## How to Use

Create your timeline inside of the `timeline.json` file. Set the `timeline_name` property for the text in the top left of the rendered image. Use `start_date` and `end_date` to set the beginning and end of the timeline and the width of the image. Events are the most important part of the timeline. Each event must contain 4 fields; 2 of which (`description` and `images`) are currently unused and therefore can be left empty. The `name` field of an event will be what actually shows on the timeline while the `date` field is where it will show up. Order matters when setting up the timeline. You must have all events listed in chronological order within `timeline.json` in order for it to render correctly. You can modify the font used in the image by dropping a TrueType Font (ttf) file in this folder and renaming it to `font.ttf`. Finally, you can render your image by double-clicking on the `run.bat` file. If you wish to check it for RATS because I know this community doesn't trust me you can open the `run.bat` file inside of a text editor such as Notepad or Visual Studio Code. All you will find is a very simple 2 lines of code that run the `render.py` script and close the batch file.

## The End Goal

This current version of the timeline creator is so that we as a community can put together the most complete history of the cts community easily without things scattered around the image (spending). The end goal of this will be having a completed `timeline.json` file containing every event in the cts community from what lead to its creation all the way to where we are today. This will allow me to create an interactive application where players can scroll along the timeline and select specific events seeing the description of the event along with some fun images and videos from that time. I have already given a little bit of a kickstart to the creation of the `timeline.json` to make it a little easier to understand how to add events to the timeline.
