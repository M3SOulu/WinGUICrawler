# Win GUI Crawler

## Intro


This tool was developed in order to compile a large-scale GUI image/metadata dataset with the purpose of using it improve GUI element identification with machine learning methods. <br> GUI element identification is an essential part of VGT (Visual GUI Testing) and RPA (Robotic Process Automation) workflows.  Recently machine learning methods have been ubiquitous in image recognition tasks, but they haven't yet become widespread in RPA and VGT applications which still mostly rely on more traditional image processing methods. Since machine learning heavily relies on sizeable amounts of data, compiling a large-scale dataset could encourage progress in the two related fields. <br>
Existing datasets only concern GUI's in the mobile and web domains, there is a lack of publicly available data in the desktop domain. In order to fill that gap a crawler was developed that automatically traverses a Windows desktop application and collects screenshots with related metadata. </br>

## Features
The backbone of this tool is based on [WinAppDriver](https://github.com/microsoft/WinAppDriver), which is a service to support Selenium-like UI Test Automation on Windows Applications.
The Win GUI Crawler has several features which will be briefly explained in this section.

- ### Windows desktop application crawling
As its name implies, the main objective of this tool is to automatically traverse a windows application and collect data. It crawls the application in a depth first manner and collects unique screenshots, thus extracting GUI images and xml metadata. Additionally all interactions are recorded in a tree where nodes signify GUI screens and edges correspond to actions taken by the crawler.

- ### Manual screenshot and metadata retrieval
This feature allows users to manually extract data from an application by keypress. It doesn't record interactions but can prove useful when wanting to extract data from a specific screen.
- ### Bounding box filter
Labels that can be extracted from the metadata might correspond to elements that are not visible in the image and thus result in wrong labels. To clean up the labels a filtering scheme is applied which helps improve labeling accuracy.

# Possible uses
-     The main goal of the tool is to gather large amounts of (partially-)annotated data, which with a subsequent fine combed manual annotation step could produce quality data for machine learning methods.​
- Another possible use can be to assist template matching based methods by automatically extracting images of GUI elements

# Limitations
- Applications which do not use native Win32 API (e.g. Gtk or HMTL-based) are incompatible, they do not provide access to all GUI element metadata.
- GUI element metadata from windows that are not linked to the main process or main application window can't be accessed.
