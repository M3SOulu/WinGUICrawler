#Takes two screens (image + gui metadata) or just one in case of root as input
#The script filters bounding boxes in order to clean them up by removing out of view or irrelevant items
import os
import cv2
import sys
from lxml import etree
import random
import numpy as np
import json
import shutil
import csv

#Needed for json output
class TreeNode(dict):
    def __init__(self, tag, name, type, offscreen, filtered_out, topleft, bottomright, children=None):
        super().__init__()
        self.__dict__ = self
        self.tag = tag
        self.name = name
        self.type = type
        self.offscreen = offscreen
        self.filtered_out = filtered_out
        self.topleft = topleft
        self.bottomright = bottomright
        self.children = list(children) if children is not None else []

#If an element doesn't have name attribute it becomes an empty string instead of None type object
def get_el_name(el):
    if 'Name' in el.attrib:
        return el.attrib['Name']
    else:
        return ""

#Recursive function that constructs a tree that can be converted to json
def recursive_json_tree(branch, element, list_el, blacklist):
    list_of_children = []
    for child in list_el:
        if child.getparent() == element:
            list_of_children.append(child)
    if len(list_of_children) == 0:
        return
    else:
        for child in list_of_children:
            tl = [int(child.attrib['x']), int(child.attrib['y'])]
            br = [tl[0]+int(child.attrib['width']), tl[1]+int(child.attrib['height'])]
            isFilteredOut = ("True" if child in blacklist else "False")
            newnode = TreeNode(child.tag, get_el_name(child), child.attrib["LocalizedControlType"],child.attrib["IsOffscreen"],isFilteredOut,tl,br)
            branch.children.append(newnode)
            recursive_json_tree(branch.children[-1],child,list_el,blacklist)

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

#retrieves a list of xpaths of gui elements
def get_xpath_list(list_of_elements):
    list_of_xpaths = []
    for el in list_of_elements:
        list_of_xpaths.append(get_unique_xpath(el))
    return list_of_xpaths

#compares the sets of elements to check whether they are the same
def detect_duplicate(current_filtered, all_filtered):
    set_current_xpaths = set(get_xpath_list(current_filtered))
    for i_filtered in all_filtered:
        set_i_xpaths = set(get_xpath_list(i_filtered))
        if set_i_xpaths == set_current_xpaths:
            return True
    return False

#Cleans the parents of offscreen elements, meaning that if an element has offscreen children they get cropped out of it's area (makes the parent bbox look nicer)
def clean_parent_offscreen(list_off_screen):
    #Keeps memory of already "seen" elements
    list_exclude = []

    #loop through all off screen items
    for el in list_off_screen:
        #if it's already been "seen" then exclude it to avoid duplicates
        if el not in list_exclude:
            #Checks if a parent exists and is on screen
            if el.getparent() != None:
                parente = el.getparent()
                if parente.attrib['IsOffscreen'] == "False":
                    if 'Name' in parente.attrib: #ignore elements without name tag, they don't produce useful bounding boxes
                        #calculates top left and bottom right corners
                        tl = [int(parente.attrib['x']), int(parente.attrib['y'])]
                        br = [tl[0]+int(parente.attrib['width']), tl[1]+int(parente.attrib['height'])]
                        if not (tl[0] == br[0] or tl[1] == br[1] or tl[0] == br[0] or tl[1] == br[1]): #Checks if it's a box, and not a line or point
                            #Compile a list of elements with the same parent
                            same_parent = []
                            for el2 in list_off_screen:
                                if el2 not in list_exclude:
                                    if el2.getparent() != None:
                                        parente2 = el2.getparent()
                                        if 'Name' in parente2.attrib: #ignore elements without name tag, they don't produce useful bounding boxes
                                            if parente2 == parente:
                                                same_parent.append(el2)
                                                list_exclude.append(el2)
                            #Take the farthers corners of all the boxes
                            tl_min = [sys.maxsize,sys.maxsize]
                            br_max = [0,0]
                            isBox = True
                            #Leaves a bounding box which excludes the offscreen area from the onscreen parent
                            for eee in same_parent:
                                tl = [int(eee.attrib['x']), int(eee.attrib['y'])]
                                br = [tl[0]+int(eee.attrib['width']), tl[1]+int(eee.attrib['height'])]
                                if not (tl[0] == br[0] or tl[1] == br[1] or tl[0] == br[0] or tl[1] == br[1]): #Checks if it's a box
                                    if tl[0]<tl_min[0]: tl_min[0] = tl[0]
                                    if tl[1]<tl_min[1]: tl_min[1] = tl[1]
                                    if br[0]>br_max[0]: br_max[0] = br[0]
                                    if br[1]>br_max[1]: br_max[1] = br[1]
                                else:
                                    isBox = False
                            if isBox:
                                tl = [int(parente.attrib['x']), int(parente.attrib['y'])]
                                br = [tl[0]+int(parente.attrib['width']), tl[1]+int(parente.attrib['height'])]
                                if tl == tl_min:
                                    if br[0] == br_max[0]:
                                        parente.attrib['y'] = str(br_max[1])
                                        parente.attrib['heigth'] = str(abs(br_max[1]-br[1]))
                                    if br[1] == br_max[1]:
                                        parente.attrib['x'] = str(br_max[0])
                                        parente.attrib['width'] = str(abs(br_max[0]-br[0]))
                                if br == br_max:
                                    if tl[1] == tl_min[1]:
                                        parente.attrib['width'] = str(abs(tl[0]-tl_min[0]))
                                    if tl[0] == tl_min[0]:
                                        parente.attrib['height'] = str(abs(tl[1]-tl_min[1]))

#Draws bounding boxes and saves image to file, from non blacklisted elements
def draw_bboxes(imgname,result_name,list_of_el,blacklist,rgb):
    #Use decode instead of imread, because it can't take unicode characters
    img = cv2.imdecode(np.fromfile(imgname,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    result = img.copy()
    index_rgb = 0
    list_on_screen = []
    #loops through non blacklisted onscreen elemnts, draws colored bounding boxes and puts them in a list
    for el in list_of_el:
        if el.attrib['IsOffscreen'] == "False":
            if el not in blacklist:
                tl = (int(el.attrib['x']), int(el.attrib['y']))
                br = (tl[0]+int(el.attrib['width']), tl[1]+int(el.attrib['height']))
                cv2.rectangle(result, tl, br, rgb[index_rgb%len(rgb)],2)
                index_rgb += 1
                list_on_screen.append(el)
    cv2.imwrite(result_name,result)
    #returns list of onscreen elements
    return list_on_screen

#Returns true if two rectangles overlap
def doOverlap(x1,y1,width1,height1,x2,y2,width2,height2):
    tl1 = (int(x1),int(y1))
    br1 = (tl1[0]+int(width1), tl1[1]+int(height1))
    tl2 = (int(x2),int(y2))
    br2 = (tl2[0]+int(width2), tl2[1]+int(height2))

    # To check if either rectangle is actually a line
    if (tl1[0] == br1[0] or tl1[1] == br1[1] or tl2[0] == br2[0] or tl2[1] == br2[1]):
        # the line cannot have positive overlap
        return False

    #area of intersecion over the smallest of the two bboxes, this way relatively small overlaps can be ignored
    IoS = intersection_over_small(tl1[0],tl1[1],br1[0],br1[1],tl2[0],tl2[1],br2[0],br2[1])

    #arbitary threshold
    if IoS > 0.15:
        return True
    else:
        return False

#Checks which elements are overlapping and returns a list of overlapping pairs
def overlap_check(list_of_on_screen):
    overlapping = []
    alreadyseen = [] #used to keep track and avoid duplicates
    for el in list_of_on_screen:
        alreadyseen.append(el)
        for el2 in list_of_on_screen:
            if el2 not in alreadyseen:
                if doOverlap(el.attrib['x'],el.attrib['y'],el.attrib['width'],el.attrib['height'],el2.attrib['x'],el2.attrib['y'],el2.attrib['width'],el2.attrib['height']):
                    overlapping.append((el,el2))
    return overlapping

#Checks whether an element is a parent of another
def check_parent(el_ch,el_pr):
    while el_ch.getparent()!=None:
        parente = el_ch.getparent()
        if parente == el_pr:
            return True
        else:
            el_ch = parente
    return False

#Checks if two elements have the same parent (only 1 level, so direct siblings)
def check_direct_sibling(el1,el2):
    if el1.getparent()!=None and el2.getparent()!=None:
        if el1.getparent() == el2.getparent():
            return True
        else:
            return False
    else:
        return False

#calculates the intersecion of two bboxes over the area of the smallest of the two
def intersection_over_small(tl1x,tl1y,br1x,br1y,tl2x,tl2y,br2x,br2y):
    xA = max(tl1x,tl2x)
    yA = max(tl1y,tl2y)
    xB = min(br1x,br2x)
    yB = min(br1y,br2y)

    # respective area of ​​the two boxes
    boxAArea=(br1x-tl1x)*(br1y-tl1y)
    boxBArea=(br2x-tl2x)*(br2y-tl2y)
    minboxArea = min(boxAArea,boxBArea)
     # overlap area
    interArea=max(xB-xA,0)*max(yB-yA,0)

    return interArea/minboxArea

#Main funtion of the script, which filters the bboxes based on previous and current screen, also avoids saving duplicates
def filter_bbox(imgname_previous,imgname_current,all_filtered,istree):
    list_of_current_el = []
    list_of_previous_el = []

    #Handles all the file names
    if istree:
        splitname_current = imgname_current.split('.png')
        filepath = splitname_current[0]
        xmlname_current  = filepath+".xml"
        nodename = filepath.split("/screenshot-")[-1]
        foldername_raw_filt = filepath.split("/raw_screens")[0]+"/raw_filtered_comparison/"+nodename
        foldername_elements = filepath.split("/raw_screens")[0]+"/elements/"+nodename+"/"
    else:
        filepath = imgname_current.split('.png')[0]
        xmlname_current  = filepath+".xml"
        filepath_split = filepath.split("raw_screens/")
        nodename = filepath_split[1]
        foldername_raw_filt = filepath_split[0]+"raw_filtered_comparison/"+nodename+"/"
        foldername_elements = filepath_split[0]+"elements/"+nodename+"/"

    if not os.path.exists(foldername_raw_filt):
        os.mkdir(foldername_raw_filt)
    if os.path.exists(foldername_elements):
        shutil.rmtree(foldername_elements)
    os.mkdir(foldername_elements)
    os.mkdir(foldername_elements+"images/")
    filepath_raw_filt = foldername_raw_filt+"/"+nodename
    filepath_elements = foldername_raw_filt+"/"+nodename

    json_txt_name_current  = filepath_raw_filt+".txt"
    result_name_current = filepath_raw_filt+"_raw"+".png"
    result_name_filtered = filepath_raw_filt+".png"

    #Prepares filenames and tree in case previous exists (not in Root)
    #If previous doesn't exists, the list stays empty and the algorithm works without any changes
    if len(imgname_previous)>0:
        splitname_previous  = imgname_previous.split('.png')
        xmlname_previous  = splitname_previous[0]+".xml"

        #Create tree of previous screen
        tree_previous = etree.parse(xmlname_previous)

        #Previous
        for elt in tree_previous.iter():
            #ignore elements without name tag, they don't produce useful bounding boxes
            if 'Name' in elt.attrib:
                list_of_previous_el.append(elt)

    #Create tree of current screen
    tree_current = etree.parse(xmlname_current)

    #Create list of elements in current screen
    for elt in tree_current.iter():
        list_of_current_el.append(elt)

    #Lists of offscreen elements
    list_of_current_off_screen =  []
    list_of_previous_off_screen =  []

    for el in list_of_current_el:
        if el.attrib['IsOffscreen'] == "True":
            list_of_current_off_screen.append(el)

    for el in list_of_previous_el:
        if el.attrib['IsOffscreen'] == "True":
            list_of_previous_off_screen.append(el)

    #Cleans up the parents of offscreen elements (makes bboxes look nicer, but isn't that significant. Works for now, if it creates issues better to remove it)
    clean_parent_offscreen(list_of_current_off_screen)
    clean_parent_offscreen(list_of_previous_off_screen)

    #List of different colors for the bboxes
    rgb = []
    for i in range(1,255,64):
        for j in range(1,255,64):
            for k in range(1,255,64):
                rgb.append((i,j,k))

    #Draws bounding boxes of all elements (no filtering, blacklist is emplty)
    list_of_current_on_screen = draw_bboxes(imgname_current,result_name_current,list_of_current_el,[],rgb)

    #Check overlap and create list of overlapping elements
    list_of_overlapping_current = overlap_check(list_of_current_on_screen)

    #Use decode instead of imread, because it can't take unicode characters
    img = cv2.imdecode(np.fromfile(imgname_current,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    result = img.copy()
    #List of blacklisted elemnts
    blacklist = []
    #Contains some non straightforward cases that get added to the blacklist later if they satisfy certain criteria
    blacklist_tough_cases = []
    #List of elements that are drawn on another file (used to draw only specific elements, mainly for debugging)
    draw_list = []

    #If two elements are overlaping, and one is a window
    #Might not be a good idead in some cases
    #Check if the window is the other elemnts parent, if not then it's probably covering it, so blacklist the other element
    """for el_pair in list_of_overlapping_current:
        isWindow0 = (el_pair[0].tag == "Window")
        isWindow1 = (el_pair[1].tag == "Window")
        if (isWindow0 and (not isWindow1)):
            if not check_parent(el_pair[1],el_pair[0]):
                blacklist.append(el_pair[1])
        if (isWindow1 and (not isWindow0)):
            if not check_parent(el_pair[0],el_pair[1]):
                blacklist.append(el_pair[0])"""

    #Direct sibling and parent-child that overlap are fine, the rest are inspected
    for el_pair in list_of_overlapping_current:
        if  ((el_pair[0] not in blacklist) and (el_pair[1] not in blacklist)):
            isParent = check_parent(el_pair[0],el_pair[1]) or check_parent(el_pair[1],el_pair[0])
            isSibling = check_direct_sibling(el_pair[0],el_pair[1])
            if isParent == False and isSibling == False:# and isWindow == False:
                #Check if one of the elements in the pair already existed in previous screen
                #If yes keep the newer one, previous elements have already been acquired, and are probably underneath the newer ones so not visible
                elpair0_equal_prev = False
                elpair1_equal_prev = False
                for prev in list_of_previous_el:
                    previous_xpath = get_unique_xpath(prev)
                    elpair_0_xpath = get_unique_xpath(el_pair[0])
                    elpair_1_xpath = get_unique_xpath(el_pair[1])

                    if previous_xpath == elpair_0_xpath:
                        elpair0_equal_prev = True
                    if previous_xpath == elpair_1_xpath:
                        elpair1_equal_prev = True

                if elpair0_equal_prev and (not elpair1_equal_prev):
                    blacklist.append(el_pair[0])
                if (not elpair0_equal_prev) and elpair1_equal_prev:
                    blacklist.append(el_pair[1])

                if elpair0_equal_prev == elpair1_equal_prev:
                    #both are either new or old, they get added to another list and evaluated later
                    blacklist_tough_cases.append(el_pair)

    for el_pair in blacklist_tough_cases:
        #Prioritise elements with content, because panes,menus,... are sometimes not visible and don't matter in the image
        type_prioritised = ["ListItem","MenuItem","Image","Button","SplitButton","TabItem","Text","HyperLink","ScrollBar","Thumb"]

        if not ((el_pair[0] in blacklist) and (el_pair[1] in blacklist)):
            if (el_pair[0].tag in type_prioritised) and (el_pair[1].tag not in type_prioritised):
                blacklist.append(el_pair[1])
            else:
                if (el_pair[1].tag in type_prioritised) and (el_pair[0].tag not in type_prioritised):
                    blacklist.append(el_pair[0])
                else:
                    DONOTHING ="DONOTHING" #filtering by size or number of overlaps doesn't always make sense, so it's better to just leave them be

    #Also add elemnts that are too small in area to blacklist, they don't correspond to visible elemnts
    for el in list_of_current_el:
        if (int(el.attrib["width"])<=5) and (int(el.attrib["height"])<=5):
            blacklist.append(el)

    index_rgb = 0
    for el in draw_list:
        tl = (int(el.attrib['x']), int(el.attrib['y']))
        br = (tl[0]+int(el.attrib['width']), tl[1]+int(el.attrib['height']))
        cv2.rectangle(result, tl, br, rgb[index_rgb%len(rgb)],2)
        cv2.circle(result, tl, 50, (0,0,0), 2)
        print(tl)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = el.tag+":"+get_el_name(el)
        textsize = cv2.getTextSize(text, font, 1, 2)[0]
        cv2.putText(result, text, (tl[0],tl[1]), font, 0.5, rgb[index_rgb%len(rgb)], 1)

    if len(draw_list)>0:
        cv2.imwrite(("draw/"+imgname_current.split("/screenshot-")[-1]).split(".png")[0]+"_draw.png",result)

    #Draw and save filtered bounding boxes
    list_of_current_filtered = draw_bboxes(imgname_current,result_name_filtered,list_of_current_el,blacklist,rgb)

    #Get the first element with no parent (tree root), should be enough to just get the first element, but it's better to be sure it's the root element
    for el in list_of_current_el:
        if (el.getparent()) == None:
            tl = [int(el.attrib['x']), int(el.attrib['y'])]
            br = [tl[0]+int(el.attrib['width']), tl[1]+int(el.attrib['height'])]
            isFilteredOut = ("True" if el in blacklist else "False")
            root = TreeNode(el.tag, get_el_name(el), el.attrib["LocalizedControlType"],el.attrib["IsOffscreen"],isFilteredOut,tl,br)
            root_el = el
            root_raw = TreeNode(el.tag, get_el_name(el), el.attrib["LocalizedControlType"],el.attrib["IsOffscreen"],isFilteredOut,tl,br)
            break


    recursive_json_tree(root,root_el,list_of_current_el,blacklist)

    with open(json_txt_name_current, 'w') as outfile:
        json.dump(root, outfile,indent=2)

    #crop to images and save in elements, also save as .csv
    img = cv2.imdecode(np.fromfile(imgname_current,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
    header = ['filename', 'tag', 'name', 'type','offscreen','filtered_out','topleft','bottomright']
    data_list = []

    for el in list_of_current_el:
        tl = [int(el.attrib['x']), int(el.attrib['y'])]
        br = [tl[0]+int(el.attrib['width']), tl[1]+int(el.attrib['height'])]
        cropped = img[tl[1]:br[1],tl[0]:br[0]]
        cropped_name = el.tag+"-"+get_el_name(el)+".png"
        count = 1
        while os.path.exists(foldername_elements+cropped_name):
            count+=1
            cropped_name = el.tag+"-"+get_el_name(el)+"("+str(count)+")"+".png"
        if cropped.size > 0:
            cv2.imwrite(foldername_elements+"images/"+cropped_name,cropped)
        isFilteredOut = ("True" if el in blacklist else "False")
        data_list.append([cropped_name,el.tag,get_el_name(el),el.attrib['LocalizedControlType'],el.attrib['IsOffscreen'],isFilteredOut,'['+str(tl[0])+','+str(tl[1])+']','['+str(br[0])+','+str(br[1])+']'])

    with open(foldername_elements+foldername_elements.split("/elements/")[-1][:-1]+".csv", 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for d in data_list:
            writer.writerow(d)

    #filtered doesn't contain duplicates
    if not detect_duplicate(list_of_current_filtered, all_filtered):
        all_filtered.append(list_of_current_filtered)
        #copy files to filtered folder
        files = [json_txt_name_current, result_name_filtered]
        direc = json_txt_name_current.split("raw_filtered_comparison")[0]

        for f in files:
            shutil.copy(f, direc+"filtered_screens")
    else:
        print("..........................")
        print("..........................")
        print("Duplicate is: ",result_name_filtered)
        print("..........................")
        print("..........................")
    return all_filtered

if __name__ == "__main__":
    filename_prev = sys.argv[1]
    filename_curr = sys.argv[2]
    directory = os.getcwd()+"/"+filename_curr.split("/")[0]+"/"
    if not os.path.exists(directory+"raw_filtered_comparison/"):
        os.mkdir(directory+"raw_filtered_comparison/")
    if not os.path.exists(directory+"elements/"):
        os.mkdir(directory+"elements/")
    if not os.path.exists(directory+"filtered_screens/"):
        os.mkdir(directory+"filtered_screens/")
    filter_bbox(filename_prev,filename_curr,[],True)
