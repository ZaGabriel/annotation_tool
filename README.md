# Bounding Box Generator Tool

A user-friendly GUI tool for generating bounding boxes to define detection areas.

This tool is constructed using OpenCV and PyQt5, allowing you to easily draw bounding boxes on an image and save the coordinates.

## Requirements

This tool has been tested with Python 3.8. The required dependencies can be installed using the following command:

```bash
pip install -r requirements.txt
```

## Usage
```bash
python tool.py
```

### Image
Click the "Open Image" button to open your image file.

### Video stream
Paste url to your video stream and click "Open Stream".

By click "Open Stream" again when video stream is running to close video stream.

Next choose classes to draw bounding box. After all you can save the bounding box by clicking "Save" button.
