# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 11:53:07 2020

@author: Job de Vogel

TO FIX:
-

What this file will do:
If a button on the arduino board is clicked, this script will find an audiofile
on the computer and play it. If multiple buttons are clicked, there will be a queue
in order of which they are clicked. Also, a potentiometer is added to change the
volume of the audio.

The files should be ordered as follows:
    - PATH TO FOLDER WITH ALL DATA
        - HOUSEMATE
            - PRIORITY (data that should be played as soon as possible)
            - All other data files
"""

import pygame #MIXER: WAV, MP3, OGG files
from pygame.locals import KEYDOWN, K_ESCAPE
import shutil
import win32con
import sys
from ctypes import windll
from pyfirmata import ArduinoNano, util
from os import system, listdir, path, rename, mkdir
from time import sleep
from random import shuffle
from datetime import datetime
from win32gui import SendMessage

print("\n")
print("Preparing Rustoord Bingo for launch...")

#LAPTOP RELATED FUNCTIONS
def TurnScreenOff():
    SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, 2)
    return

def TurnScreenOn():
    SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, -1)
    return

def ShutDown():
    system('shutdown -s')
    
def GetTime(): #in minutes from 00:00
    now = datetime.now()
    hours = now.strftime("%H")
    minutes = now.strftime("%M")
    return int(hours) * 60 + int(minutes)

def GetRealTime(): #in hours_minutes
    now = datetime.now()
    hours = now.strftime("%H")
    minutes = now.strftime("%M")
    return str(hours) + "h_" + minutes + "m"

def ErrorMessage(Error):
    pygame.mixer.quit()
    pygame.quit()
    TurnScreenOn()
    
    print("\n")
    print("Lieve huisgenoot, waarom moet alles nou altijd kapot???")
    
    #write error file
    nameErrorFile = "ErrorOccured_at_" + str(GetRealTime()) + ".txt"
    file = open(nameErrorFile, "w")
    file.write(str(datetime.now()))
    file.write("\n")
    file.write(str(Error))
    file.close()
    
    #show countdown for shutdown
    t = 10
    for sec in range(t , 0 , -1):   
        sys.stdout.write("\r")
        sys.stdout.write("ZELFDESTRUCTIE IN " + "{:2} SECONDEN!!!".format(sec))
        sys.stdout.flush()
        sleep(1)
    
    print("\n" + "\n" + "Nee hoor, grapje, wordt opnieuw opgestart in ongeveer 3 minuten")
    sleep(5)

    sys.exit()
    return

##############################################

#Try to initiate all globale variables, if something goes wrong, write an error to script folder
try:
    #global variables
    HOUSEMATES = ["Struis", "Pumba", "Ekkie", "Muis", "Rups", "Mhorr", "Wants", "Mona"]
    #AUDIOPATH = "C:/Users/Job de Vogel/Documents/TU Delft/Python programming/Arduino_Project/Audio_Files/"
    #IMAGEPATH = "C:/Users/Job de Vogel/Documents/TU Delft/Python programming/Arduino_Project/Image_Files/"
    AUDIOPATH = "C:/Users/Rustoord Bingo/Google Drive/Arduino_Project/Welcome_Bingo/Audio_Files/"
    IMAGEPATH = "C:/Users/Rustoord Bingo/Google Drive/Arduino_Project/Welcome_Bingo/Image_Files/"
    AUDIO_FILE_TYPES = [".mp3", "MP3", ".wav", ".WAV", ".ogg", ".OGG"]
    IMAGE_FILE_TYPES = [".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png", ".GIF", ".gif", ".BMP", ".bmp", ".PCX", ".pcx", ".TGA", ".tga", ".TIF", ".tif", ".LBM", ".lbm", ".PBM", ".pbm", ".XPM", ".xpm"]
    PLAYTIME = 15000 #ms
    SHUTDOWNTIME = 1320 #time in minutes (ENTER 1500 IF YOU DON'T WANT TO SHUT DOWN LAPTOP)
    
    #Arduino variables
    port = "COM3"
    board = ArduinoNano(port)
    
    #Pygame visuals variables
    BLACK = (0, 0, 0)
    
    #for PMW, iterator that will be used to set the connection with the Arduino board
    it = util.Iterator(board)
    it.start()
    
    #Housemate connected to pin
    StruisButton = board.get_pin('d:2:i')
    PumbaButton = board.get_pin('d:3:i')
    EkkieButton = board.get_pin('d:4:i')
    MuisButton = board.get_pin('d:5:i')
    RupsButton = board.get_pin('d:7:i')
    MhorrButton = board.get_pin('d:8:i')
    WantsButton = board.get_pin('d:9:i')
    MonaButton = board.get_pin('d:10:i')
    
    LED = board.get_pin('d:13:o')
    LED.write(0)
    
    VolumeMeter = board.get_pin('a:7:i')
    
    LastImage = ""
except Exception as Error:
    board.exit()
    ErrorMessage(Error)

##################################################

#SCRIPT RELATED FUNCTIONS:
def CheckFileSystem(HOUSEMATES):
    for Housemate in HOUSEMATES:
        #If a folder doesn't exist: make it
        #Audiofolder:
        if not path.exists(AUDIOPATH):
            mkdir(AUDIOPATH)
        if not path.exists(AUDIOPATH + Housemate):
            mkdir(AUDIOPATH + Housemate)
            mkdir(AUDIOPATH + Housemate + "/Priority")
            mkdir(AUDIOPATH + Housemate + "/Archive")
        if not path.exists(AUDIOPATH + Housemate + "/Priority"):
            mkdir(AUDIOPATH + Housemate + "/Priority")
        if not path.exists(AUDIOPATH + Housemate + "/Archive"):
            mkdir(AUDIOPATH + Housemate + "/Archive")
        
        #Imagefolder
        if not path.exists(IMAGEPATH):
            mkdir(IMAGEPATH)
        if not path.exists(IMAGEPATH + Housemate):
            mkdir(IMAGEPATH + Housemate)
            mkdir(IMAGEPATH + Housemate + "/Priority")
            mkdir(IMAGEPATH + Housemate + "/Archive")
        if not path.exists(IMAGEPATH + Housemate + "/Priority"):
            mkdir(IMAGEPATH + Housemate + "/Priority")
        if not path.exists(IMAGEPATH + Housemate + "/Archive"):
            mkdir(IMAGEPATH + Housemate + "/Archive")

#finds the audiofile of the housemate, priority indicates that it has to be played as soon as possible
def findAudioFilename(AUDIOPATH, housemate, priority):
    if priority:
        try:
            files = listdir(AUDIOPATH + housemate + "/Priority")   #find the files in the folder
            
            FilesAvailable = False #Variable that checks if there are files in the folder
            
            for file in files:
                if path.isfile(AUDIOPATH + housemate + "/Priority/" + file) and any(TYPE in file for TYPE in AUDIO_FILE_TYPES):   #for all files, if file (not folder), return PATH and filename
                    FilesAvailable = True
                    return AUDIOPATH + housemate + "/Priority/" + file
                    break
            
            if FilesAvailable is False: #if no file available, return False
                return False
        
        except IndexError: #if no files in path, return false
            return False
    
    #ELSE: do the same but without priority
    else:
        try:
            files = listdir(AUDIOPATH + housemate)
            shuffle(files)

            FilesAvailable = False
            
            for file in files:
                if path.isfile(AUDIOPATH + housemate + "/" + file) and any(TYPE in file for TYPE in AUDIO_FILE_TYPES):
                    FilesAvailable = True
                    return AUDIOPATH + housemate + "/" + file
                    break
            
            if FilesAvailable is False:
                return False
            
        except IndexError:
            return False

#Pygame visuals functions
def GetScreenResolution():
    windll.user32.SetProcessDPIAware()
    
    monitorWidth = windll.user32.GetSystemMetrics(0)
    monitorHeigth = windll.user32.GetSystemMetrics(1)
        
    return monitorWidth, monitorHeigth

#return random image from housemate folder
def LoadImage(IMAGEPATH, Housemate, MONITORWIDTH, MONITORHEIGTH, LastImage = False):
    
    PriorityFiles = listdir(IMAGEPATH + Housemate + "/Priority")
    NormalFiles = listdir(IMAGEPATH + Housemate)
    
    #shuffle the normalfiles
    shuffle(NormalFiles)
        
    #initially, no files are available in priority and normal folder
    PriorityFilesAvailable = False
    NormalFilesAvailable = False
    
    #check if Priorityfiles are available
    for file in PriorityFiles:
        if any(TYPE in file for TYPE in IMAGE_FILE_TYPES):
            PriorityFilesAvailable = True
            break

    image = False
    
    #if no PriorityFiles are available, check if normalfiles are available
    if not PriorityFilesAvailable:
        for file in NormalFiles:
            if any(TYPE in file for TYPE in IMAGE_FILE_TYPES):
                NormalFilesAvailable = True
                break

    #if PriorityFiles are available, image is first file in folder that is supported
    if PriorityFilesAvailable and not pygame.mixer.music.get_busy():
        for file in PriorityFiles:
            if any(TYPE in file for TYPE in IMAGE_FILE_TYPES):
                image = pygame.image.load(IMAGEPATH + Housemate + "/Priority/"  + file)
                LastImage = file
                break
    #if not, if normalfiles are available, image is first file in folder that is supported and isn't the last image
    elif NormalFilesAvailable:
        for file in NormalFiles:
            if any(TYPE in file for TYPE in IMAGE_FILE_TYPES) and file != LastImage:
                image = pygame.image.load(IMAGEPATH + Housemate + "/"  + file)
                LastImage = file
                break
        
        if not image:
            file = LastImage
            image = pygame.image.load(IMAGEPATH + Housemate + "/"  + file)
        
    #if image is available in directory
    if image:
        #find the dimensions of the image
        imageWidthOrig = image.get_width()
        imageHeigthOrig = image.get_height()
        
        #find which dimension is closest to monitordimension
        WidthDifference = abs(int(MONITORWIDTH - imageWidthOrig))
        HeigthDifference = abs(int(MONITORHEIGTH - imageHeigthOrig))
        
        #based on which dimension differenc is greatest, scale with correct factor
        if MONITORWIDTH > imageWidthOrig and MONITORHEIGTH < imageHeigthOrig:
            factor = MONITORHEIGTH / imageHeigthOrig
            image = pygame.transform.scale(image, (int(factor * imageWidthOrig), MONITORHEIGTH))
        elif MONITORWIDTH < imageWidthOrig and MONITORHEIGTH > imageHeigthOrig:
            factor = MONITORWIDTH / imageWidthOrig
            image = pygame.transform.scale(image, (MONITORWIDTH, int(factor * imageHeigthOrig)))
        elif WidthDifference > HeigthDifference and WidthDifference != 0 and HeigthDifference !=0:
            factor =  MONITORWIDTH/ imageWidthOrig
            image = pygame.transform.scale(image, (MONITORWIDTH, int(factor * imageHeigthOrig)))
        elif WidthDifference < HeigthDifference and WidthDifference != 0 and HeigthDifference !=0:        
            factor = MONITORHEIGTH / imageHeigthOrig
            image = pygame.transform.scale(image, (int(factor * imageWidthOrig), MONITORHEIGTH))
        elif WidthDifference == HeigthDifference:
            factor = MONITORHEIGTH / imageHeigthOrig
            image = pygame.transform.scale(image, (int(factor * imageWidthOrig), MONITORHEIGTH))
        
    return image, LastImage

def RenameAndArchive(file, destinationPath, Housemate):
    FileWithDate = file.replace(".", "_" + str(GetRealTime()) + ".")
    
    #try to move the file to the archive
    try:
        rename(file, FileWithDate)
        shutil.move(FileWithDate, destinationPath + Housemate + "/Archive/")                    
    except Exception as Error:
        print(Error)
        pass
    return

##################################################

#MAIN LOOP
def main(AUDIOPATH, IMAGEPATH, HOUSEMATES, board):  
    AudioQueue = []
    PriorityQueue = {}
    ImagePriorityQueue = {}
    
    
    #Dictionary that checks if button is pressed continuously:
    ButtonTracker = {"Struis": StruisButton.read(), "Pumba": PumbaButton.read(), "Ekkie": EkkieButton.read(), "Muis": MuisButton.read(), "Rups": RupsButton.read(), "Mhorr": MhorrButton.read(), "Wants": WantsButton.read(), "Mona": MonaButton.read()}
    
    print("Checking data...")
    #checks if someone removed all the folders... ;)
    CheckFileSystem(HOUSEMATES)  
    
    #COUNTDOWN
    sleep(1)
    print("3...")
    sleep(1)
    print("2..")
    sleep(1)
    print("1.")
    sleep(1)
    print("Launch!")
    sleep(0.5)
    
    #Turn the screen off and set the ScreenChecker to Off for later in the main loop to check
    
    TurnScreenOff()
    ScreenChecker = "Off"
        
    #pygame visuals variables
    RESOLUTION = GetScreenResolution()
    MonitorWidth = RESOLUTION[0]
    MonitorHeigth = RESOLUTION[1]
    
    #Pygame Initialization
    pygame.init()
    display_surface = pygame.display.set_mode((MonitorWidth, MonitorHeigth))
    pygame.display.set_caption('Image')
    display_surface.fill(BLACK)
        
    #main loop
    try:
        print("Running...")
        pygame.mixer.init()
        
        LastImage = ""
        
        while True:
            #read all the buttons
            ActiveButtons = [StruisButton.read(), PumbaButton.read(), EkkieButton.read(), MuisButton.read(), RupsButton.read(), MhorrButton.read(), WantsButton.read(), MonaButton.read()]

            #Change volume according to potentiometer
            Volume = VolumeMeter.read()
            if Volume is not None:
                pygame.mixer.music.set_volume(Volume)
            
            #for every button, if clicked, check if music is already played, if not: play music of housemate, else: add to queue
            for i, button in enumerate(ActiveButtons):
                Housemate = HOUSEMATES[i]
                
                if button and ButtonTracker[Housemate] == 0:    #check if button is pressed and check if it's not pressed continuously
                    
                    #Message that someone came home with time
                    print(str(Housemate) + " came home at " + str(GetRealTime()) + "!")   
                    
                    #Pygame update screen image
                    display_surface.fill(BLACK)
                                        
                    try:
                        imageData = LoadImage(IMAGEPATH, Housemate, MonitorWidth, MonitorHeigth, LastImage)
                    except FileNotFoundError:
                        CheckFileSystem(HOUSEMATES)
                        imageData = LoadImage(IMAGEPATH, Housemate, MonitorWidth, MonitorHeigth, LastImage)
                                        
                    image = imageData[0]
                    LastImage = imageData[1]
                    
                    if LastImage in listdir(IMAGEPATH + Housemate + "/Priority/"):
                        ImagePriorityQueue[Housemate] = LastImage
                    
                    if LastImage not in ImagePriorityQueue and image:
                        display_surface.blit(image, (MonitorWidth/2 - image.get_width()/2, MonitorHeigth/2 - image.get_height()/2))

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            break
                        if event.type == KEYDOWN:
                            # Was it the Escape key? If so, stop the loop.
                            if event.key == K_ESCAPE:
                                pygame.quit()
                                break
                    pygame.display.flip()
                    
                    #Pygame initiate audio
                    if not pygame.mixer.music.get_busy():
                        #check if there are audiofiles in the priority folder
                        Audio = findAudioFilename(AUDIOPATH, Housemate, True)                       
                        #if audio available
                        if Audio:
                            #if audio of housmate is not in AudioQueue and audio is playable by mixer
                            if Housemate not in AudioQueue :
                                pygame.mixer.music.load(Audio)
                                pygame.mixer.music.play()
                                AudioQueue.append(Housemate)
                                PriorityQueue[Housemate] = Audio
                                                                    
                        else:
                            ###Check if a file is available, if not CheckFileDirectories
                            try:
                                Audio = findAudioFilename(AUDIOPATH, Housemate, False)
                            except FileNotFoundError:
                                CheckFileSystem(HOUSEMATES)
                                Audio = findAudioFilename(AUDIOPATH, Housemate, False)
                            if Audio:
                                if Housemate not in AudioQueue:
                                    pygame.mixer.music.load(Audio)
                                    pygame.mixer.music.play()
                                    AudioQueue.append(Housemate)

                    else:
                        #No priority audio will be played, housemate probably already walked to his room
                        ###Check if a file is available, if not CheckFileDirectories
                        try:
                            Audio = findAudioFilename(AUDIOPATH, Housemate, False)
                        except FileNotFoundError:
                            CheckFileSystem(HOUSEMATES)
                            Audio = findAudioFilename(AUDIOPATH, Housemate, False)
                        if Audio:
                            if Housemate not in AudioQueue:
                                pygame.mixer.music.queue(Audio)
                                AudioQueue.append(Housemate)
                    
                #Here the Buttontracker is updated, which holds 1 if the button is pressed continuosly
                if not button:
                    ButtonTracker[Housemate] = 0
                else:
                    ButtonTracker[Housemate] = 1
            
            #move priority to archive and delete queues
            if AudioQueue and not pygame.mixer.music.get_busy():
                AudioQueue = []
                if PriorityQueue:
                    for Housemate, Audio in PriorityQueue.items():
                        pygame.mixer.music.unload()
                        RenameAndArchive(Audio, AUDIOPATH, Housemate)                        
                        PriorityQueue = {}
            
            if ImagePriorityQueue and not pygame.mixer.music.get_busy():
                for Housemate, Image in ImagePriorityQueue.items():
                    Image = IMAGEPATH + Housemate + "/Priority/" + Image
                    RenameAndArchive(Image, IMAGEPATH, Housemate)
                    ImagePriorityQueue = {}
                    
            #if playtime longer than x, fadeout audio
            if PLAYTIME:
                if pygame.mixer.music.get_pos() > PLAYTIME:
                    pygame.mixer.music.fadeout(5000)
                        
            #turn LED on if music is being played
            if pygame.mixer.music.get_busy():
                LED.write(1)
            else:
                LED.write(0)

            
            #LAPTOP RELATED FUNCTIONS
            #if music is being played and screen is off, turn screen on
            
            if ScreenChecker == "Off":
                if pygame.mixer.music.get_busy() == 1:
                    TurnScreenOn()
                    ScreenChecker = "On"
            
            if ScreenChecker == "On":
                if pygame.mixer.music.get_busy() == 0:
                    TurnScreenOff()
                    ScreenChecker = "Off"
            
            #if time is later than SHUTDOWNTIME, turn laptop off
            time = GetTime()
            
            if time >= SHUTDOWNTIME:
                system('shutdown -s')
            elif time % 60 == 0:
                CheckFileSystem(HOUSEMATES)
            
            LED.write(1)
            sleep(0.01)
            LED.write(0)
    except KeyboardInterrupt:
        pygame.mixer.quit()
        board.exit()
        pygame.quit()
        TurnScreenOn()

###INITIATE MAIN LOOP
try:
    main(AUDIOPATH, IMAGEPATH, HOUSEMATES, board)
except Exception as Error:
    board.exit()
    ErrorMessage(Error)
