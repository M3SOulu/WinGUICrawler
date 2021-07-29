#This script goes through the graph and filters the bounding boxes using gui_filter_bbox.py
import pickle
import xml.etree.ElementTree as ET
import os
import gui_filter_bbox

#directory where the screenshots (.png and .xml) are saved
directory = '%s/' % os.getcwd()+"screens_temp/"

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

#Removes characters that can't be used in filenames
def replace_illegal_char(input):
    output = input
    #Replace illegal filename characters
    for ch in ['<','>',":","\"","/","\\","|","?","*"]:
        if ch in output:
            output = output.replace(ch,"")
    return output

rootNodeName = "Root"
#Loads graph
if os.path.isfile(directory+"graphs"):
    with open(directory+"graphs","rb") as fp:
        graph = pickle.load(fp)
        nodes = pickle.load(fp)
    rootNode = nodes[rootNodeName]
else:
    print("No file found")

end_flag = False
last = ""
current = rootNodeName
#Keeps track of which nodes have already been traversed
visited = []
#Keeps going until the end_flag is set
while (not end_flag):
    if current not in visited:
        if current != rootNodeName:
            #counter keeps track of the naming
            last_counter = 0
            isPreviousScreen = False
            len_last = 0
            #If there are some gaps in the screenshots, the graphs skips them until it finds the next screenshot
            while isPreviousScreen == False:
                last_counter += 1
                len_last += (len(current.split('_+_')[-last_counter])+3)
                last = current[:-len_last]
                imgname_previous = directory+"screenshot-"+replace_illegal_char(nodes[last].name)+".png"
                isPreviousScreen = os.path.isfile(imgname_previous)
            imgname_current = directory+"screenshot-"+replace_illegal_char(nodes[current].name)+".png"
            #Applies bbox filtering
            gui_filter_bbox.filter_bbox(imgname_previous,imgname_current)
        else:
            #In case of Root, there is no previous screen
            last = ""
            imgname_current = directory+"screenshot-"+replace_illegal_char(nodes[current].name)+".png"
            gui_filter_bbox.filter_bbox("",imgname_current)
        print("Filtering: ",nodes[current].name,"        ",nodes[last].name if last != "" else last)
        #Add node to visited
        visited.append(current)

    found_child_to_visit_flag = False
    #Loops thorugh all possible children of current node and picks the first non visited
    for next_node_candidate in graph[current]:
        if (nodes[next_node_candidate].screen):
            if (next_node_candidate not in visited):
                #proceeds traversal with chosen node
                current = next_node_candidate
                found_child_to_visit_flag = True
                break

    #This means there is a dead end, go back to the previous node, unless root
    #if in root then end
    if found_child_to_visit_flag == False:
        #If there are no candidates from traversal from Root it means that the whole graph has been covered
        if current == rootNodeName:
            end_flag = True
        else:
            #goes back up the tree by one step
            len_last = len(current.split('_+_')[-1])+3
            current = current[:-len_last]
