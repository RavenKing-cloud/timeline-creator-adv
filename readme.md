# Timeline Creator

Made by [@TauCommands](https://github.com/TenCommands) & [@RavenKing-cloud](https://github.com/RavenKing-cloud)

## Requirements

PIL
```pip install --upgrade PILLOW```

PyQt5
```pip install --upgrade PyQt5```

## How to use

1. Run the `run.bat` file within the project folder
2. Click `Open JSON File` and select a JSON file containing the proper values or click `Create New Timeline` to create a new timeline
3. You can now see your timeline image in the window which you can find in the `export` folder
4. You can edit your open timeline directly through the interface by editing or adding events
5. We recommend that you edit and create new timelines through the interface but you can also edit the timeline using the `json` file syntax below:

```json
{
    "timeline_name": "Example Timeline Name",
    "start_date": [1,1,2024],
    "end_date": [1,1,2025],
    "events": [
            {
                "name": "Event 1",
                "date": [2,29,2024],
                "description": "",
                "images": []
            },
            {
                "name": "Event 2",
                "date": [3,3,2024],
                "description": "",
                "images": []
            },
            {
                "name": "Event 3",
                "date": [4,24,2024],
                "description": "",
                "images": []
            }
    ]
}
```

The `start` and `end` dates are given a 6 month padding to the edge of the image so you can see the year markers better.

This example leaves you with this:

![export/example.png](export/example.png)

### Side Notes

- When selecting `images` you must make sure that it is in the `/images` dir and this is the core storage for images, do not delete images from here! All pathing to images is relative to this dir and the `main.py` script.

### Todo

- [X] toolbar
  - [X] create timeline file
  - [X] add event to timeline
    - [X] modify logic to sort and overwrite json data
- [X] integrate sort logic to main
- [X] select event from toolbar to view tooltip
  - [X] pop out display with image and (live edit*)
    - [X] delete button with confirmation
    - [X] make the display update and reload when event is edited and saved
- [X] ~~fix single line list encoder to be a function in src~~
- [X] modify render code to prevent overlapping
  - [X] event overlap
  - [X] year text overlap
- [ ] final gui enhancements
  - [X] darkmode
  - [ ] custom fonts
  - [ ] custom icon
- [ ] make timeline render images in the background
  - [ ] make this be a toggle*
- [ ] add fully comprehensive documentation
  - [ ] inline docs
  - [ ] final readme
