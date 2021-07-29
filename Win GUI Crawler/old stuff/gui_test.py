
import unittest
from appium import webdriver
import time
import pyautogui
import pickle
import xml.etree.ElementTree as ET
import time #time.perf_counter()
import os
from win32 import win32gui
import keyboard


if __name__ == '__main__':

    #opens the application via webdriver
    desired_caps = {}
    #desired_caps["app"] = r"C:\Users\watas\AppData\Roaming\Zoom\bin\Zoom.exe"
    desired_caps["app"] = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
    #desired_caps["app"] = r"C:\Program Files\Notepad++\notepad++.exe"
    desired_caps["appium:ms:waitForAppLaunch"] = 5
    driver = webdriver.Remote(command_executor='http://127.0.0.1:4724',desired_capabilities= desired_caps)
    #get all gui metadata as xml string
    time.sleep(5)
    #hwnd = int(driver.current_window_handle,16)
    #win32gui.SetForegroundWindow(hwnd)
    #time.sleep(5)

    counter = 0
    while True:
        keyboard.wait('s')
        time.sleep(2)
        source = driver.page_source

        #take a screenshot
        directory = '%s/' % os.getcwd()
        file_name = 'screenshot'+str(counter)+'.png'
        driver.save_screenshot(directory + file_name)

        #write gui metadata
        xml_file = open("screenshot"+str(counter)+".xml","wb")
        xml_file.write(source.encode("utf-16"))
        xml_file.close()
        counter+=1
        time.sleep(3)

    driver.quit()
