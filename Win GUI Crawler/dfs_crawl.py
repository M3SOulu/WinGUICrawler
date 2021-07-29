#This script is used to take crawl an application in dfs fashion, while gathering image screenshots and gui metadata
#Each execution of the crawl function has the crawler going from root to an end of the graph. The crawler is made persistent with saved dicts
#Run the crawler until Root dies (meaning the application has been explored completely) with argument 0, and N times with argument N being a positive integer

from appium import webdriver
import time
import pyautogui
import pickle
import time
import os
from win32 import win32gui
import keyboard
from lxml import etree
import cv2
import random
import pickle
import numpy as np
import psutil
import sys
import traceback
from win32api import GetSystemMetrics



class Node(object):
    '''Creates a node object'''

    def __init__(self, path, name, action, click_list): #action might be useless
        '''Defines x and y variables'''
        #name of the node
        self.name = name
        #path of the node, made from appende xpaths of actions
        self.path = path
        #last action taken to get to this node
        self.action = action
        #has it already been visited?
        self.visited = False
        #List of clickable actions that can be take at this node
        self.click_list = click_list
        #Alive means that either the node and/or it's children haven't been explored yet
        self.alive = True
        #Is there a screenshot of the node?
        self.screen = False
        #Keeps track of how many times the crawler passed through this node
        self.counter = 0

    #list of clickables to string
    def clk_list_to_str(self):
        stringhy = "["
        for clk in self.click_list:
            stringhy += clk
            stringhy += ","
        return stringhy[:-1]+"]"

    def __str__(self):
        return "(%s,%s,%s,%s,%s,%s,%s)"%(self.path,self.name, self.action, self.visited, self.alive,self.clk_list_to_str(),self.counter)

#Functions to save and load dictionaries
def save_dict(input_dict,filename):
    with open(filename,'w') as f:
        f.write(json.dumps(input_dict))

def load_dict(filename):
    with open(filename) as f:
        f.write(json.dumps(input_dict))
    output_dict = json.loads(f.read())
    return output_dict

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
        if (elt.tag in clickable_items) and (elt.attrib['IsEnabled']=="True") and ('Name' in elt.attrib):
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

    #When windows minimise the coordinates can get weirdly high numbers
    if window_w < 1.5*GetSystemMetrics(0) and window_h < 1.5*GetSystemMetrics(1):
        #Take a screenshot and crop it to fit the application
        img = pyautogui.screenshot(region=(window_x,window_y,window_w,window_h))
        #Write image to file
        print("Name before saving:")
        print(imgname)
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
        return True
    else:
        #If the coordinates are larger than the screen (meaning something strange happened), the screenshot is not taken
        return False

#Removes characters that can't be used in filenames
def replace_illegal_char(input):
    output = input
    #Replace illegal filename characters
    for ch in ['<','>',":","\"","/","\\","|","?","*"]:
        if ch in output:
            output = output.replace(ch,"")
    return output

def xpath_to_name(name):
    split_path = name.split("_+_")
    for part_xpath in split_path[1:]:
        print((part_xpath.split("[@")[1]).split("\']")[0])
    return name

#Retrieves an xpath for the element
def get_unique_xpath(element):
    el_xpath = ""
    finished = False
    list_path = []
    list_path.append(element.tag+"[@Name = \'"+element.attrib['Name']+"\']")
    while not finished:
        if element.getparent() == None:
            finished = True
        else:
            element = element.getparent()
            list_path.append(element.tag)
    for el in list_path[::-1]:
        el_xpath += "/"+el
    return el_xpath

#Crawler function
def crawl():
    #directory where the screenshots (.png and .xml) will be saved
    directory = '%s/' % os.getcwd()+"screens_temp/"

    #List of the types of elements that are considered clickable, i.e. permit interaction and could produce new screens
    clickable_items = ["Button","SplitButton","MenuItem","TabItem","ListItem","CheckBox"]

    #A set that keeps track of all clickable items that have been seen during traversal
    union_traversed = set([])

    #opens the application via webdriver
    desired_caps = {}
    #desired_caps["app"] = r"C:\Users\watas\AppData\Roaming\Zoom\bin\Zoom.exe"
    #desired_caps["app"] = "C:\Windows\System32\explorer.exe"
    #desired_caps["app"] = r"C:\Windows\System32\mspaint.exe"
    desired_caps["app"] = r"Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
    #desired_caps["app"] = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    #desired_caps["app"] = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
    #desired_caps["app"] = r"C:\Program Files\Oracle\VirtualBox\VirtualBox.exe"
    #desired_caps["app"] = r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
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

    rootNodeName = "Root"

    #Checks if the graph already exists and loads it
    if os.path.isfile(directory+"graphs"):
        with open(directory+"graphs","rb") as fp:
            graph = pickle.load(fp)
            nodes = pickle.load(fp)
        rootNode = nodes[rootNodeName]
    else:
        #Creates new graph and adds root node
        #Graph will be made of two dicts, one containing adjacency list and one containing node info
        graph = {}
        nodes = {}
        rootNode = Node(rootNodeName,rootNodeName,None,None) #Path, Name, last action, list of unique clickables
        nodes[rootNodeName] = rootNode

    #Flag that signifies a dead end in the tree traversal, meaning the crawler needs to stop
    DeadEnd = False
    current_node = rootNode

    if not rootNode.alive:
        #If root is dead, it means that the whole application has been visited, the crawler is done
        print("Root is dead")
        return True
    else:
        while DeadEnd == False:
            #If it's not been visited take metadata and info to store in node, if it's unique take a screen otherwise declare it dead
            print("--------------------------")
            print("Currently at node: ",current_node.name,"\n")
            current_node.counter += 1
            if current_node.visited == False:
                #get metdata
                try:
                    xmlsource, clickable, els, rect = take_metadata(driver,clickable_items)
                except Exception as error:
                    #If the application crashes unexpectedly (errors or close has been clicked), the node is killed
                    print("Caught exception, window might be closed")
                    print(traceback.format_exc())
                    current_node.alive = False
                    DeadEnd = True
                    #Quits and save the graph
                    driver.quit()
                    with open(directory+"graphs","wb") as fp:
                        pickle.dump(graph,fp)
                        pickle.dump(nodes,fp)
                    return False
                #update node info
                current_node.visited = True
                #create children and add to graph
                child_nodes = []

                #create list of unique clickables and save in node and create children
                #they are considered unique if encountered for the first time during traversal
                unique_list = list(set(clickable).difference(union_traversed))
                current_node.click_list = unique_list
                #Create all it's children that are reach with their respective clickable actions
                for clickable_el in unique_list:
                    #parse the name from path
                    clt = clickable_el.split("[@Name = \'")
                    clickable_el_name = clt[0].split("/")[-1]+"-"+clt[1][:-2]

                    #Create child
                    child_name = current_node.name+"_+_"+clickable_el_name
                    child_path = current_node.path+"_+_"+clickable_el
                    child_nodes.append(child_path)
                    nodes[child_path] = Node(child_path,child_name,clickable_el,None)
                graph[current_node.path]=child_nodes

                #If there are no unique clickables kill node, otherwise take screen
                if len(unique_list) == 0:
                    current_node.alive = False
                    DeadEnd = True
                else:
                    screen_taken = take_screen(driver,replace_illegal_char(current_node.name),xmlsource,els,rect)
                    current_node.screen = screen_taken
                    if screen_taken:
                        print("Taking screen of: ",current_node.name)
                    else:
                        #If there are issues during image acquisition the node is killed
                        print("Not taking screen")
                        DeadEnd = True
                        current_node.alive = False

            #update union traversed
            union_traversed = union_traversed.union(set(current_node.click_list))
            print("Possible actions are: ",current_node.click_list)

            #Check if all children are dead, if not, go to first alive child
            AllDead = True
            max_counter =  sys.maxsize

            #Goes through all children and picks the least visited one (ensuring the tree gets traversed in a uniform order)
            for child_path in graph[current_node.path]:
                child_node = nodes[child_path]
                if child_node.alive == True:
                    AllDead = False
                    if child_node.counter < max_counter:
                        traverse_next = child_node
                        max_counter = child_node.counter

            #continue traversal with next node if there is at least 1 alive child
            if AllDead == False:
                last_node = current_node
                current_node = traverse_next
                current_node_action = (current_node.path).split("_+_")[-1]
                current_node.action = current_node_action
                try:
                    #Click the clikable element that takes the application to the next node
                    driver.find_element_by_xpath(current_node_action).click()
                    print("Clicking: ",current_node_action)
                    time.sleep(2)
                except Exception as error:
                    #Kill node if errors happen (for example if the elemnt doesn't exist)
                    print("Caught exception, no clickable element")
                    print(traceback.format_exc())
                    current_node.alive = False
                    current_node = last_node
            else:
                #If all children are dead, then the father node is killed and a dead end is reached
                current_node.alive = False
                DeadEnd = True
                print("************************************")
                print("Dead End reached")
                print("************************************")

    #Terminate the application and exit driver
    p = psutil.Process(int(processId))
    p.terminate()
    time.sleep(1)
    driver.quit()
    #Save the graphs
    with open(directory+"graphs","wb") as fp:
        pickle.dump(graph,fp)
        pickle.dump(nodes,fp)
    return False

if __name__ == '__main__':
    #If input is an integer N>0, then execute the crawler N times
    #if the input is N=0, then execute crawler until root dies
    iterations = int(sys.argv[1])
    Root_dead_flag = False
    if iterations > 0:
        for i in range(0,iterations):
            print("********************************")
            print("*                              *")
            print("*    Crawling application      *")
            print("*                              *")
            print("********************************")
            Root_dead_flag = crawl()
            if Root_dead_flag:
                print("********************************")
                print("*                              *")
                print("*   Root Dead, Crawling over   *")
                print("*                              *")
                print("********************************")
                break
    else:
        if iterations == 0:
            while not Root_dead_flag:
                print("********************************")
                print("*                              *")
                print("*    Crawling application      *")
                print("*                              *")
                print("********************************")
                Root_dead_flag = crawl()
            print("********************************")
            print("*                              *")
            print("*   Root Dead, Crawling over   *")
            print("*                              *")
            print("********************************")
        else:
            print("Please input a non negative integer")
