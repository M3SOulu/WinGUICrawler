#This script is used to visualise the application exploration tree
#It produces an .svg file with the graph visualisation
import pickle
import xml.etree.ElementTree as ET
import os
from graphviz import Digraph

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

#Functions to load dictionaries
def load_dict(filename):
    with open(filename) as f:
        f.write(json.dumps(input_dict))
    output_dict = json.loads(f.read())
    return output_dict

#Removes characters that can't be used in filenames
def replace_illegal_char(input):
    output = input
    #Replace illegal filename characters
    for ch in ['<','>',":","\"","/","\\","|","?","*"]:
        if ch in output:
            output = output.replace(ch,"")
    return output

rootNodeName = "Root"
#Load graph
if os.path.isfile(directory+"raw_screens/graphs"):
    with open(directory+"raw_screens/graphs","rb") as fp:
        graph = pickle.load(fp)
        nodes = pickle.load(fp)
    rootNode = nodes[rootNodeName]
else:
    print("No file found")

#Declare graph
G = Digraph(name='gui_graph', node_attr={'pad': '1','nodesep': '2','ranksep': '2'})

#Add dict to graphviz graph
for item in graph.items():
    node_name = replace_illegal_char(nodes[item[0]].name)+" | "+str(nodes[item[0]].counter)+" | "+("Alive" if nodes[item[0]].alive else  "Dead")+" | "+("Screen" if nodes[item[0]].screen else  "No Screen")
    G.node(node_name)
    for e in item[1]:
        edge_node_name = replace_illegal_char(nodes[e].name)+" | "+str(nodes[e].counter) +" | "+("Alive" if nodes[e].alive else  "Dead")+" | "+("Screen" if nodes[e].screen else  "No Screen")
        G.edge(node_name,edge_node_name)
#Render the graph
G.render(directory+'app_graph', format='svg',view=False)
