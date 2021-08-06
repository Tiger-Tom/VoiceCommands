# Imports
import os
import sys
if os.name == 'nt':
    comm = '"'+sys.executable.replace('pythonw', 'python')+'" -m pip install pipwin'
    print (comm)
    os.system(comm)
    comm = '"'+sys.executable.replace('pythonw', 'python')+'" -m pipwin pyaudio'
comm = '"'+sys.executable.replace('pythonw', 'python')+' -m pip install keyboard SpeechRecognition'
print (comm)
os.system(comm)
import keyboard
import speech_recognition as sr
import io
import socketlib
import time
from Colors import bcolors

# Recognizer
spR = sr.Recognizer()

# Config #
recordStartKey = 'f6' #Can only be 1 key
recordStopKey = 'f6' #Can only be 1 key
recordSendKeys = 'f7' #Can be multiple keys combined together
recordDelKeys = 'f8' #Can be multiple keys combined together

# Setup keyboard

#  Setup macros
def recordStartF():
    keyboard.unhook_all_hotkeys() #Disable all hotkeys for safety
    while keyboard.is_pressed(recordStartKey): #Wait until the key is not being pressed
        pass
    data = None
    try:
        data = recognizeAudio()
    except Exception as e:
        print (bcolors.FAIL+'An error occured while reading audio ('+str(e)+')'+bcolors.ENDC)
    if data:
        try:
            print (data+' >>> [server]')
            client.send(data, doRecv=False)
            command_list.append(data)
        except Exception as e:
            print (bcolors.FAIL+'An error occured while sending data ('+str(e)+')'+bcolors.FAIL)
    while keyboard.is_pressed(recordStopKey): #Wait until the key is not being pressed
        pass
    setupHotkeys() #Re-enable hotkeys
def recordSendF():
    if len(command_list) > 0:
        keyboard.unhook_all_hotkeys() #Disable all hotkeys for safety
        keyboard.write(command_list[0], delay=0.005)
        print (bcolors.OKCYAN+'Sent "'+command_list.pop(0)+'"'+bcolors.ENDC)
        setupHotkeys() #Re-enable hotkeys
    else:
        print (bcolors.WARNING+'Cannot send, as the command list is empty'+bcolors.ENDC)
    client.send('⌘delete_first', doRecv=False)
def recordDelF():
    if len(command_list) > 0:
        print (bcolors.OKCYAN+'Deleted "'+command_list.pop()+'"'+bcolors.OKCYAN)
    else:
        print (bcolors.WARNING+'Cannot delete, as the command list is empty'+bcolors.ENDC)
    client.send('⌘delete_last', doRecv=False)

#   Hotkey setup
def setupHotkeys():
    keyboard.add_hotkey(recordStartKey, recordStartF)
    keyboard.add_hotkey(recordSendKeys, recordSendF)
    keyboard.add_hotkey(recordDelKeys, recordDelF)

#  Setup recognizer
def record(source, duration=None, offset=None): #Modified from an answer on https://stackoverflow.com/questions/62361776/stop-speech-recognition-on-keypress
    """
    Records up to ``duration`` seconds of audio from ``source`` (an ``AudioSource`` instance) starting at ``offset`` (or at the beginning if not specified) into an ``AudioData`` instance, which it returns.

    If ``duration`` is not specified, then it will record until there is no more audio input.
    """
    assert isinstance(source, sr.AudioSource), "Source must be an audio source"
    assert source.stream is not None, "Audio source must be entered before recording, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"

    frames = io.BytesIO()
    seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
    elapsed_time = 0
    offset_time = 0
    offset_reached = False
    while True:  # loop for the total number of chunks needed
        if offset and not offset_reached:
            offset_time += seconds_per_buffer
            if offset_time > offset:
                offset_reached = True

        buffer = source.stream.read(source.CHUNK)
        if len(buffer) == 0: break

        if offset_reached or not offset:
            elapsed_time += seconds_per_buffer
            if keyboard.is_pressed(recordStopKey):
                pressed = True
                break

            frames.write(buffer)

    frame_data = frames.getvalue()
    frames.close()
    return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
spR.record = record #Hijack the "record" function

def getAudio():
    with sr.Microphone() as source:
        print (bcolors.OKGREEN+'Getting input'+bcolors.ENDC)
        audio = spR.record(source)
        print (bcolors.OKBLUE+'Finished recording'+bcolors.ENDC)
    return audio
def recognizeAudio():
    return spR.recognize_google(getAudio())

# Setup socket
port = socketlib.find_open_port()
print ('Port has been found: '+str(port))
client = socketlib.client()

# Start listener
print ('Starting listener')
comm = 'start '+sys.executable.replace('pythonw', 'python')+' "'+os.getcwd()+'/VoiceCommands-Display.py" -port '+str(port)
print (comm)
os.system(comm)
time.sleep(1) #Wait for listener to setup, just to be safe

# Start socket
print ('Connecting to listener server on port '+str(port))
client.connect('localhost', port)
client.sock.setblocking(False) #Make the socket non-blocking

# Main
command_list = []
setupHotkeys()
print ('Setup complete!\nThis window can now be minimized.')
print ('Press CTRL+C to close')
while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        print ('Program closed')
        client.send('⌘stop_server', doRecv=False)
        break
