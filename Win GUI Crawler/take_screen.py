#This script is used to take screenshots (image and gui metadata) of the chosen application
from appium import webdriver
import time
import pyautogui
import pickle
from lxml import etree
import time
import os
from win32 import win32gui
import keyboard
import cv2
import pickle
import numpy as np
import psutil
import sys
import traceback
from datetime import datetime
from win32api import GetSystemMetrics

#directory where the screenshots (.png and .xml) will be saved
directory = '%s/' % os.getcwd()+"taken_screens/"

#This function extracts gui metadata from the application
def take_metadata(driver,clickable_items):
    time.sleep(1)
    #winappdriver extracts the metadata and copies it into a string
    source = driver.page_source
    time.sleep(1)

    #initial most top left and most bottom right corners, used to get the bounding rectanle containing all gui elements (in order to crop unneccessary parts of the screenshot image)
    tl_x = sys.maxsize
    tl_y = sys.maxsize
    br_x = 0
    br_y = 0

    #gui elements are put into a list by iterating over the xml tree
    list_elements = []
    clickable_list = []

    tree = etree.fromstring(source.encode('utf-16'))
    for elt in tree.iter():
        list_elements.append(elt.attrib)
        if (elt.tag in clickable_items) and (elt.attrib['IsEnabled']=="True"):
            clickable_list.append(get_unique_xpath(elt))

        #Take the furthest top left and furthest bottom right corners from all onscreen elements
        if elt.attrib["IsOffscreen"] == "False":
            temp_tl_x = int(elt.attrib['x'])
            temp_tl_y = int(elt.attrib['y'])
            temp_br_x = temp_tl_x + int(elt.attrib['width'])
            temp_br_y = temp_tl_y + int(elt.attrib['height'])
            if temp_tl_x < tl_x: tl_x = temp_tl_x
            if temp_tl_y < tl_y: tl_y = temp_tl_y
            if temp_br_x > br_x: br_x = temp_br_x
            if temp_br_y > br_y: br_y = temp_br_y

    #Add the offset to all elements in the xml, so as to have the most top left corner at (0,0)
    for elt in tree.iter():
        elt.attrib['x'] = str(int(elt.attrib['x']) - tl_x)
        elt.attrib['y'] = str(int(elt.attrib['y']) - tl_y)
    source = etree.tostring(tree,encoding="unicode", method="xml")
    #returns the metadata, a list of gui elements and coordinate of the application bounding box
    return source, clickable_list, list_elements, (tl_x, tl_y, br_x, br_y)

#This function takes an image screenshot, writes it and also writes the metadata onto an xml file
def take_screen(driver,appended_name,xmlmeta,list_of_elements,rect):
    imgname = directory +'screenshot-'+appended_name+'.png'
    #get the top left corner of the focused window relative to the whole screen
    pos = driver.get_window_position()
    #add the offset to the top left corner and calulate width/height
    window_x = pos['x']+rect[0]
    window_y = pos['y']+rect[1]
    window_w = abs(rect[0]-rect[2])
    window_h = abs(rect[1]-rect[3])
    #When windows minimise the coordinates can get weirdly high numbers, this ensures the screenshot exists (even if sometimes it's a 1px placeholder)
    if window_w > 1.5*GetSystemMetrics(0):
        window_w = 1
        window_x = 0
    if window_h > 1.5*GetSystemMetrics(1):
        window_h = 1
        window_y = 0
    #Take a screenshot and crop it to fit the application
    img = pyautogui.screenshot(region=(window_x,window_y,window_w,window_h))
    #Write image to file
    img.save(imgname)

    #write gui metadata to file
    xml_file = open(directory+"screenshot-"+appended_name+".xml","wb")
    xml_file.write(xmlmeta.encode("utf-16"))
    xml_file.close()

    #Write an image with bounding boxes of all elements superimposed on it
    result_name = directory+"bbox_result-"+appended_name+".png"
    #Use decode instead of imread, because it can't take unicode characters
    img = cv2.imdecode(np.fromfile(imgname,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    result = img.copy()
    for el in list_of_elements:
        tl = (int(el['x']), int(el['y']))
        br = (tl[0]+int(el['width']), tl[1]+int(el['height']))
        cv2.rectangle(result, tl, br, (0,0,255),2)
    cv2.imwrite(result_name,result)

if __name__ == '__main__':
    #opens the application via webdriver
    desired_caps = {}
    #desired_caps["app"] = r"C:\Users\watas\AppData\Roaming\Zoom\bin\Zoom.exe"
    #desired_caps["app"] = "C:\Windows\System32\explorer.exe"
    #desired_caps["app"] = r"C:\Windows\System32\mspaint.exe"
    #desired_caps["app"] = r"Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
    #desired_caps["app"] = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    #desired_caps["app"] = r"C:\Program Files\Oracle\VirtualBox\VirtualBox.exe"
    desired_caps["app"] = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
    #desired_caps["app"] = r"C:\Program Files\XnConvert\xnconvert.exe"
    #desired_caps["app"] = r"C:\Program Files\TeamViewer\TeamViewer.exe"
    #desired_caps["app"] = r"C:\Program Files\Notepad++\notepad++.exe"

    #Wait 2s, to make sure application has opened and possible splash screens are gone (some apps may require more time)
    desired_caps["appium:ms:waitForAppLaunch"] = 2

    #Connect to winappdriver on localhost and port 4724
    driver = webdriver.Remote(command_executor='http://127.0.0.1:4724',desired_capabilities= desired_caps)

    time.sleep(1)

    #In case there is a splash screen it switches to main window after it's gone
    rootwindow = driver.window_handles[0]
    driver.switch_to.window(rootwindow)
    time.sleep(1)

    #Sets window to foreground
    hwnd = int(rootwindow,16)
    win32gui.SetForegroundWindow(hwnd)

    #Extract process ID from metadata, it is needed to close the application
    source = driver.page_source
    time.sleep(1)
    tree = etree.fromstring(source.encode('utf-16'))
    processId = tree.attrib['ProcessId']

    #If prompt the user to take a screenshot or exit
    while True:
        print("Press \"p\" to take a screen and \"e\" to exit")
        input = keyboard.read_key()
        print("You pressed: "+input)
        if input == "e":
            break
        if input == "p":
            #Take screenshot
            xmlsource, clickable, els, rect = take_metadata(driver,[]) #clickable items is not needed here, but still kept to have take_metadata same as in crawler
            date_time = datetime.now().strftime("%m%d%Y%H%M%S")
            take_screen(driver,date_time,xmlsource,els,rect)
            print("Screenshot taken")

    #Terminate the application and exit driver
    p = psutil.Process(int(processId))
    p.terminate()
    time.sleep(1)
    driver.quit()
    exit()
