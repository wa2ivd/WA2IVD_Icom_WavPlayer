# Icom_Wav_Player

# Project Description
This is a GUI based Python script that will .wav files recorded by Icom radios.  These .wav files can be played by any audio player that support .wav files.  This script provides additional features to extract and display metadata embedded in the files.
This program will play all of the .wav files sequentially in a selected folder.  The metadata window displays the data for the currently playing file.  The time data is displayed as a real-time running clock based on the recorded time.

The Icom Metadata is stored in the TITLE and COMMENT tag fields of the file.  The Python taglib is used to read the metadata fields.
The audio player from the pygame library is used to play the file audio.

## Development details
This is my first attempt at writing a GUI using Python and also my first time using libraries to handle .wav files.  I only have a casual familiarity with Python.  So this was very much a "learn as I go" project.
The code is NOT well organized.  I used ChatGPT to write a lot of the GUI code snippets to help me learn the Python code necessary to create a GUI.  I then tweaked and adjusted to the code to get the functionality I needed.
The user interface is simple and I'm sure could be improved upon, but it gets the job done.

# UI details
Use the Open Folder option in the File Menu.
Select a folder that has .wav files from an Icom radio.

<strong>Play All</strong> Plays all files from the beginning.  Clicking on any file first will start playing from that file.

<strong>Skip</strong> skips immediately to the end of the current file.

<strong>Pause</strong> and <strong>Stop</strong> behave as you would expect.

The Wave File Metadata window shows all available data for the file currently playing.

Error checking is very limited.

