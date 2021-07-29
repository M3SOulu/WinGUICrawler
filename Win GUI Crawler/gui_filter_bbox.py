#Takes two screens (image + gui metadata) or just one in case of root as input
#The script filters bounding boxes in order to clean them up by removing out of view or irrelevant items
import os
import cv2
import sys
from lxml import etree
import random

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
    img = cv2.imread(imgname)
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

#Main funtion of the script, which filters the bboxes based on previous and current screen
def filter_bbox(imgname_previous,imgname_current):
    #Handles all the file names
    list_of_current_el = []
    list_of_previous_el = []
    cavolo_current = imgname_current.split('.png')
    xmlname_current  = cavolo_current[0]+".xml"
    result_name_current = cavolo_current[0]+"_bbox_result"+".png"
    result_name_filtered = cavolo_current[0]+"_bbox_result_filtered"+".png"

    #Prepares filenames and tree in case previous exists (not in Root)
    #If previous doesn't exists, the list stays empty and the algorithm works without any changes
    if len(imgname_previous)>0:
        cavolo_previous  = imgname_previous.split('.png')
        xmlname_previous  = cavolo_previous[0]+".xml"
        result_name_previous = cavolo_previous[0]+"_bbox_result"+".png"

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
        #ignore elements without name tag, they don't produce useful bounding boxes
        if 'Name' in elt.attrib:
            #if elt.attrib['Name'] != "":
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

    img = cv2.imread(imgname_current)
    result = img.copy()
    #List of blacklisted elemnts
    blacklist = []
    #Contains some non straightforward cases that get added to the blacklist later if they satisfy certain criteria
    blacklist_tough_cases = []
    #List of elements that are drawn on another file (used to draw only specific elements, mainly for debugging)
    draw_list = []

    #If two elements are overlaping, and one is a window
    #Check if the window is the other elemnts parent, if not the it's probably covering it, so blacklist the other element
    for el_pair in list_of_overlapping_current:
        isWindow0 = (el_pair[0].tag == "Window")
        isWindow1 = (el_pair[1].tag == "Window")
        if (isWindow0 and (not isWindow1)):
            if not check_parent(el_pair[1],el_pair[0]):
                blacklist.append(el_pair[1])
        if (isWindow1 and (not isWindow0)):
            if not check_parent(el_pair[0],el_pair[1]):
                blacklist.append(el_pair[0])

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
    #Used to draw bboxes in the draw_list (mostly for debugging)
    index_rgb = 0
    for el in draw_list:
        tl = (int(el.attrib['x']), int(el.attrib['y']))
        br = (tl[0]+int(el.attrib['width']), tl[1]+int(el.attrib['height']))
        cv2.rectangle(result, tl, br, rgb[index_rgb%len(rgb)],2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = el.tag+":"+el.attrib['Name']
        textsize = cv2.getTextSize(text, font, 1, 2)[0]
        cv2.putText(result, text, (tl[0],tl[1]), font, 0.5, rgb[index_rgb%len(rgb)], 1)

    if len(draw_list)>0:
        cv2.imwrite(("draw/"+imgname_current.split("/screenshot-")[-1]).split(".png")[0]+"_draw.png",result)

    #Draw and save filtered bounding boxes
    list_of_current_filtered = draw_bboxes(imgname_current,result_name_filtered,list_of_current_el,blacklist,rgb)

if __name__ == "__main__":
    filename_prev = sys.argv[1]
    filename_curr = sys.argv[2]
    filter_bbox(filename_prev,filename_curr)
