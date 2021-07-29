import xml.etree.ElementTree as ET
import os
import cv2
import sys

if __name__ == '__main__':
    #print(time.perf_counter()-start)
    list_of_elements = []
    imgname = sys.argv[1]
    cavolo = imgname.split('.')
    xmlname = cavolo[0]+".xml"
    result_name = "bbox_result"+cavolo[0][-1]+".png"

    tree = ET.parse(xmlname)
    for elt in tree.iter():
        list_of_elements.append(elt.attrib)

    img = cv2.imread(imgname)
    result = img.copy()

    for el in list_of_elements:
        if el['IsOffscreen'] == "False":
            tl = (int(el['x']), int(el['y']))
            br = (tl[0]+int(el['width']), tl[1]+int(el['height']))
            cv2.rectangle(result, tl, br, (0,0,255),2)
            #print(el)
    #cv2.imwrite(result_name,result)
    cv2.imshow('Window',result)
    cv2.waitKey(0)
