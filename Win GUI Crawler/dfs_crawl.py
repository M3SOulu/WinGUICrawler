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

#directory where the screenshots (.png and .xml) will be saved
directory = '%s/' % os.getcwd()+"screens_temp/"

class Node(object):
    '''Creates a node object'''

    def __init__(self, path, name, action, click_list, el_list): #action might be useless
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
        #List of unique elements present at this node
        self.el_list = el_list
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
    list_elements_xpath = []
    clickable_list = []

    tree = etree.fromstring(source.encode('utf-16'))
    for elt in tree.iter():
        list_elements.append(elt.attrib)
        list_elements_xpath.append(get_unique_xpath(elt))
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
    return source, clickable_list, list_elements, list_elements_xpath, (tl_x, tl_y, br_x, br_y)

#This function takes an image screenshot, writes it and also writes the metadata onto an xml file
def take_screen(driver,appended_name,xmlmeta,list_of_elements,rect):
    imgname = directory+"raw_screens/" +'screenshot-'+appended_name+'.png'
    #get the top left corner of the focused window relative to the whole screen
    pos = driver.get_window_position()
    #add the offset to the top left corner and calulate width/height
    window_x = pos['x']+rect[0]
    window_y = pos['y']+rect[1]
    window_w = abs(rect[0]-rect[2])
    window_h = abs(rect[1]-rect[3])

    #limits width and height to screen size (actually better to leave it wider just in case)
    if window_x < -GetSystemMetrics(0):
        window_w = window_w + window_x
        window_x = 0
    if window_y < -GetSystemMetrics(1):
        window_h = window_h + window_y
        window_y = 0
    if abs(window_w) > GetSystemMetrics(0)*2:
        window_w = GetSystemMetrics(0)*2-window_x
    if abs(window_h) > GetSystemMetrics(1)*2:
        window_h = GetSystemMetrics(1)*2-window_y

    #Take a screenshot and crop it to fit the application
    img = pyautogui.screenshot(region=(window_x,window_y,window_w,window_h))
    #Write image to file
    print("Name before saving:")
    print(imgname)
    img.save(imgname)

    #write gui metadata to file
    xml_file = open(directory+"raw_screens/"+"screenshot-"+appended_name+".xml","wb")
    xml_file.write(xmlmeta.encode("utf-16"))
    xml_file.close()

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
    if 'Name' in element.attrib:
        list_path.append(element.tag+"[@Name = \'"+element.attrib['Name']+"\']")
    else:
        list_path.append(element.tag)
    while not finished:
        if element.getparent() == None:
            finished = True
        else:
            element = element.getparent()
            if 'Name' in element.attrib:
                list_path.append(element.tag+"[@Name = \'"+element.attrib['Name']+"\']")
            else:
                list_path.append(element.tag)
    for el in list_path[::-1]:
        el_xpath += "/"+el
    return el_xpath


#Crawler function
def crawl():
    if not os.path.exists(directory+"/raw_screens"):
        os.mkdir(directory+"/raw_screens")
    #List of the types of elements that are considered clickable, i.e. permit interaction and could produce new screens
    clickable_items = ["Button","SplitButton","MenuItem","TabItem","ListItem"]

    #A set that keeps track of all clickable items that have been seen during traversal
    union_traversed_clickables = set([])
    union_traversed_elements = set([])

    #opens the application via webdriver
    desired_caps = {}
    #desired_caps["app"] = r"C:\Users\watas\AppData\Roaming\Zoom\bin\Zoom.exe"
    desired_caps["app"] = r"C:\Windows\System32\mspaint.exe"
    #desired_caps["app"] = r"Microsoft.WindowsCalculator_8wekyb3d8bbwe!App"
    #desired_caps["app"] = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
    #desired_caps["app"] = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
    #desired_caps["app"] = r"C:\Program Files\Oracle\VirtualBox\VirtualBox.exe"
    #desired_caps["app"] = r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
    #desired_caps["app"] = r"C:\Program Files\XnConvert\xnconvert.exe"
    #desired_caps["app"] = r"C:\Program Files\TeamViewer\TeamViewer.exe"
    #desired_caps["app"] = r"C:\Program Files\GIMP 2\bin\gimp-2.10.exe"

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
    if os.path.isfile(directory+"/raw_screens/"+"graphs"):
        with open(directory+"/raw_screens/"+"graphs","rb") as fp:
            graph = pickle.load(fp)
            nodes = pickle.load(fp)
        rootNode = nodes[rootNodeName]
    else:
        #Creates new graph and adds root node
        #Graph will be made of two dicts, one containing adjacency list and one containing node info
        graph = {}
        nodes = {}
        rootNode = Node(rootNodeName,rootNodeName,None,None,None) #Path, Name, last action, list of unique clickables
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
                    xmlsource, clickable, els, els_xpath, rect = take_metadata(driver,clickable_items)
                except Exception as error:
                    #If the application crashes unexpectedly (errors or close has been clicked), the node is killed
                    print("Caught exception, window might be closed")
                    print(traceback.format_exc())
                    current_node.alive = False
                    DeadEnd = True
                    #Quits and save the graph
                    driver.quit()
                    with open(directory+"/raw_screens/"+"graphs","wb") as fp:
                        pickle.dump(graph,fp)
                        pickle.dump(nodes,fp)
                    return False
                #update node info
                current_node.visited = True
                #create children and add to graph
                child_nodes = []

                #create list of unique clickables and save in node and create children
                #they are considered unique if encountered for the first time during traversal
                unique_clickable_list = list(set(clickable).difference(union_traversed_clickables))
                current_node.click_list = unique_clickable_list
                #same for other elements
                unique_elements_list = list(set(els_xpath).difference(union_traversed_elements))
                current_node.el_list = unique_elements_list
                #Create all it's children that are reach with their respective clickable actions
                for clickable_el in unique_clickable_list:
                    #parse the name from path
                    clt = clickable_el.split("[@Name = \'")
                    clt2 = clt[-1][:-2]
                    clt1 = clt[-2].split("/")[-1]
                    clickable_el_name = clt1+"-"+clt2

                    #Create child
                    child_name = current_node.name+"_+_"+clickable_el_name
                    child_path = current_node.path+"_+_"+clickable_el
                    child_nodes.append(child_path)
                    nodes[child_path] = Node(child_path,child_name,clickable_el,None,None)
                graph[current_node.path]=child_nodes

                #If there are no new unique clickales, kill node
                if len(unique_clickable_list) == 0:
                    current_node.alive = False
                    DeadEnd = True

                #If there are new unique elements take screen
                if len(unique_elements_list) != 0:
                    take_screen(driver,replace_illegal_char(current_node.name),xmlsource,els,rect)
                    current_node.screen = True
                    print("Taking screen of: ",current_node.name)

            #update union traversed
            union_traversed_clickables = union_traversed_clickables.union(set(current_node.click_list))
            print("Possible actions are: ",current_node.click_list)
            union_traversed_elements = union_traversed_elements.union(set(current_node.el_list))

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
    with open(directory+"/raw_screens/"+"graphs","wb") as fp:
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
