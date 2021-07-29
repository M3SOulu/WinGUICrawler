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
import xml.etree.ElementTree as ET
import cv2
import random
import pickle
import numpy as np
import psutil
import sys

directory = '%s/' % os.getcwd()+"screens_temp/"
clickable_items = ["Button","SplitButton","MenuItem","TabItem"] #,"ListItem"]
Restricted = ["Minimise","Maximise","Minimise the Ribbon","Close","Exit"] #Minimise ribbon alters rootnode structure
union_traversed = set([])

class Node(object):
    '''Creates a node object'''

    def __init__(self, name, action, visited,alive, click_list): #action might be useless
        '''Defines x and y variables'''
        self.name = name
        self.action = action
        self.visited = visited
        self.click_list = click_list
        self.alive = alive
        self.counter = 0

    def clk_list_to_str(self):
        stringhy = "["
        for clk in self.click_list:
            stringhy += clk
            stringhy += ","
        return stringhy[:-1]+"]"

    def __str__(self):
        return "(%s,%s,%s,%s,%s,%s)"%(self.name, self.action, self.visited, self.alive,self.clk_list_to_str(),self.counter)

def save_dict(input_dict,filename):
    with open(filename,'w') as f:
        f.write(json.dumps(input_dict))

def load_dict(filename):
    with open(filename) as f:
        f.write(json.dumps(input_dict))
    output_dict = json.loads(f.read())
    return output_dict

def take_metadata(driver):
    time.sleep(1)
    source = driver.page_source
    time.sleep(1)

    #put elements from xml in list
    list_elements = []
    clickable_list = []
    tree = ET.ElementTree(ET.fromstring(source))
    for elt in tree.iter():
        list_elements.append(elt.attrib)
        if (elt.tag in clickable_items) and (elt.attrib['IsEnabled']=="True") and (elt.attrib['Name'] not in Restricted) : #Maybe its ok or maybe useless to check isEnabled
            clickable_list.append(elt.attrib['Name'].replace("\"",""))
    return source, clickable_list, list_elements

def take_screen(driver,appended_name,xmlmeta,list_of_elements):
    #take a screenshot
    imgname = directory +'screenshot-'+appended_name+'.png'
    #pos = driver.get_window_position()
    #size = driver.get_window_size()
    #img = pyautogui.screenshot(region=(pos['x'],pos['y'],size['width'],size['height']))
    #img.save(imgname)

    driver.save_screenshot(imgname)# with winappdriver, doesn't pick up item tab in paint

    #write gui metadata
    xml_file = open(directory+"screenshot-"+appended_name+".xml","wb")
    xml_file.write(xmlmeta.encode("utf-16"))
    xml_file.close()

    result_name = directory+"bbox_result-"+appended_name+".png"
    #img = cv2.imread(imgname) imread can't take unicode characters
    img = cv2.imdecode(np.fromfile(imgname,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    result = img.copy()

    for el in list_of_elements:
        #if el['IsOffscreen'] == "False":
        tl = (int(el['x']), int(el['y']))
        br = (tl[0]+int(el['width']), tl[1]+int(el['height']))
        cv2.rectangle(result, tl, br, (0,0,255),2)
    cv2.imwrite(result_name,result)
    time.sleep(1)

if __name__ == '__main__':

    #opens the application via webdriver
    desired_caps = {}
    #desired_caps["app"] = r"C:\Users\watas\AppData\Roaming\Zoom\bin\Zoom.exe"
    #desired_caps["app"] = "C:\Windows\System32\explorer.exe"
    #desired_caps["app"] = r"C:\Windows\System32\mspaint.exe"
    #desired_caps["app"] = r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE"
    #desired_caps["app"] = r"C:\Windows\System32\calc.exe"
    desired_caps["app"] = r"Root"
    #desired_caps["appium:ms:waitForAppLaunch"] = 5
    driver = webdriver.Remote(command_executor='http://127.0.0.1:4724',desired_capabilities= desired_caps)
    #hand16 = driver.current_window_handle
    #print(hand16)
    #print(int(hand16,16))
    #print(hex(int(hand16,16)))

    #get all gui metadata as xml string
    #hwnd = int(driver.current_window_handle,16)
    #win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    print("Attached to root")
    #In case there is a splash screen it switches to main window after it's gone
    #rootwindow = driver.window_handles[0]
    #print(driver.window_handles)
    #exit()
    #driver.switch_to.window(rootwindow)
    time.sleep(1)

    #Sets window to foreground
    #hwnd = int(rootwindow,16)
    #win32gui.SetForegroundWindow(hwnd)

    #source = driver.page_source
    #time.sleep(1)

    #tree = ET.ElementTree(ET.fromstring(source))
    #root = tree.getroot()
    #processId = root.attrib['ProcessId']
    xmlsource, clickable, els = take_metadata(driver)
    print("Got metadata")
    ciaone = ""
    for elt in els:
        if (elt['LocalizedControlType'] =="window"):
            print(elt['Name'])
            ciaone = elt['Name']

    ciao = driver.find_element_by_name(ciaone)
    handle_ciao = ciao.get_attribute("NativeWindowHandle")
    print(handle_ciao)
    driver.switch_to.window(hex(int(handle_ciao)))
    xmlsource, clickable, els = take_metadata(driver)
    for el in els:
        print(el)
    time.sleep(1)
    exit()
    #tree = ET.ElementTree(ET.fromstring(source))
    #root = tree.getroot()
    #processId = root.attrib['ProcessId']
    xmlsource, clickable, els = take_metadata(driver)
    ciaone = ""
    for elt in els:
        if (elt['LocalizedControlType'] =="window"):
            print(elt['Name'])
    exit()
    rootNodeName = "Root"
    #Checks if the graph already exists and loads it
    if os.path.isfile(directory+"graphs"):
        with open(directory+"graphs","rb") as fp:
            graph = pickle.load(fp)
            nodes = pickle.load(fp)
        rootNode = nodes[rootNodeName]
    else:
        #Creates new graph and adds root node
        #Graph will be made of two dicts, one containingadjacency list and one containing node info
        graph = {}
        nodes = {}
        rootNode = Node(rootNodeName,None,False,True,None) #Name, last action, visited, alive, list of unique clickables
        nodes[rootNodeName] = rootNode

    DeadEnd = False
    current_node = rootNode
    while DeadEnd == False:
        #If it's not been visited take metadata and info to store in node, if it's unique take a screen otherwise declare it dead
        print("--------------------------")
        print("Currently at node: ",current_node.name,"\n")
        print("Current windows: ",driver.window_handles,"\n")
        current_node.counter += 1
        if current_node.visited == False:
            #get metdata
            xmlsource, clickable, els = take_metadata(driver)
            #update node info
            current_node.visited = True
            #create children and add to graph
            child_nodes = []

            #create list of unique clickables and save in node and create children
            unique_list = list(set(clickable).difference(union_traversed))
            current_node.click_list = unique_list
            for clickable_el in unique_list:
                child_name = current_node.name+"_+_"+clickable_el
                child_nodes.append(child_name)
                nodes[child_name] = Node(child_name,clickable_el,False,True,None)
            graph[current_node.name]=child_nodes

            #If there are no unique clickables kill node, otherwise take screen
            if len(unique_list) == 0:
                current_node.alive = False
                DeadEnd = True
            else:
                take_screen(driver,current_node.name,xmlsource,els)
                print("Taking screen of: ",current_node.name)
                exit()
        #update union traversed
        union_traversed = union_traversed.union(set(current_node.click_list))
        print("Possible actions are: ",current_node.click_list)
        #Check if all children are dead, if not, go to first alive child
        AllDead = True
        max_counter =  sys.maxsize

        for child_name in graph[current_node.name]:
            child_node = nodes[child_name]
            if child_node.alive == True:
                AllDead = False
                if child_node.counter < max_counter:
                    traverse_next = child_node
                    max_counter = child_node.counter

        """for child_name in graph[current_node.name]:
            child_node = nodes[child_name]
            if child_node.alive == True:
                AllDead = False
                traverse_next = child_node
                break"""

        #continue traversal with next node
        if AllDead == False:
            last_node = current_node
            current_node = traverse_next
            current_node_action = (current_node.name).split("_+_")[-1]
            current_node.action = current_node_action
            #print("Click this shit: ",current_node_action)
            try:
                driver.find_element_by_name(current_node_action).click()
                time.sleep(1)
            except:
                print("Caught exception, no clickable element")
                current_node.alive = False
                current_node = last_node
        #         last_node.alive = False
        #         print(last_node.name)
        #         print(last_node.alive)
        else:
            current_node.alive = False
            DeadEnd = True
            print("************************************")
            print("Dead End reached")
            print("************************************")

    p = psutil.Process(int(processId))
    p.terminate()
    time.sleep(1)
    driver.quit()
    #saves the graphs and exit
    with open(directory+"graphs","wb") as fp:
        pickle.dump(graph,fp)
        pickle.dump(nodes,fp)
    exit()
