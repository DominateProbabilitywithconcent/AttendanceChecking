## Pre-requisites

- Python 3.11+
- CMake 4.0+
- Visual Studio for C++

## Install dependencies

Please view the `requirements.txt` file for the exact versions of the dependencies.

```bash
pip install -r requirements.txt
```

## Usage instructions

This program does not provide any data sets to recognize faces with,
you'll need to provide your own data sets.

1. Capture image files containing faces/portraits of your attendees.
2. Name the files with the student's name and save them in the `known_faces` folder as `.jpg` or `.png` files.
3. Your computer must have a webcam connected to it.
4. Run the program.

## Run program

When running the program, you can use the `--debug` flag to enable debug print statements.

Without debug mode:
```bash
python main.py
```

With debug mode:
```bash
python main.py --debug
```
