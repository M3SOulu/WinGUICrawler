# Win GUI Crawler

## Intro

This tool was developed in order to compile a large-scale gui image/metadata database with the purpose of using this database to improve gui elements identification with machine learning methods. Existing databases only concern mobile and web gui's, there is no large-scale database in the Desktop domain. In order to fill that gap a crawler was developed that automatically traverses a Windows Desktop application (using Win32 API) and collects screenshots with relative metadata. </br>
The backbone of this tool is based on [WinAppDriver](https://github.com/microsoft/WinAppDriver), which is a service to support Selenium-like UI Test Automation on Windows Applications.  



## Installation
/(Maybe add conda yml dependancies file)

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependancies (assuming you have python3 installed).

```bash
pip install Appium-Python-Client
pip install pyautogui
pip install pywin32==225
pip install keyboard
pip install opencv-python
pip install psutil
pip install lxml
```
Install Windows Application Driver from https://github.com/microsoft/WinAppDriver

## Usage

This project contains several scripts with different functionalities, for instance:
- Taking image/metadata screenshot by keypress
- Depth first search automated crawling of an application for image/metadata screenshots
- Visualisation of the application traversal graph
- Filtering of gui elements that are not visible

Before running any python scripts that employ WinAppDriver (those which take screenshots), it needs to run and listen on an IP socket.
Run WinAppDriver.exe from the installation directory (E.g. C:\Program Files (x86)\Windows Application Driver) with port number set at 4724
```bash
WinAppDriver.exe 4724
```
There several scripts in this project. Let's go through each one and their usage.

- Taking screenshots by keypress is possible with **take_screen.py**, everything will be saved in the *./take_screen* directory unless differently specified. Before running it, the Windows application under test needs to be specified under *desired_caps["app"]* (either by automation Id or exe location). To run mspaint for example:
```Python
desired_caps["app"] = r"C:\Windows\System32\mspaint.exe"
```
To run the scipt, firstly make sure to have WinAppDriver listening on port 4724 in the background, and run:
```Python
python take_screen.py
```
After waiting for several seconds the prompt will ask for a keypress, pressing "p" takes a screenshot and pressing "e" exits the script. After taking a screenshot wait for a couple of seconds for the prompt to ask again before taking another one.

- The crawler is implemented in **dfs_crawl.py**, similarly to the previous script, unless differently specified everything gets saved in the *./screens*_temp directory. Furthermore the same things apply with regards to WinAppDriver running in background and desired_caps["app"] being set to the desired application. After making sure everything is set, run the crawler:
```Python
python dfs_crawl.py
```
Each execution will make it go from Root to the end of a branch of the traversal graph. To fully crawl an app, just run the crawler several times (depends on application, at least several hundred executions are needed). For example to run it 100 times use:
```Python
for /L %n in (1,1,100) do python dfs_crawl.py
```
When the crawler has explored the whole application the root node will be killed and "Root is dead" will be printed. This script produces images, xml metadata and a graph which is saved as two dictionaries in the file *graphs*.

(Maybe add a script that automatically runs the crawler until "Root is dead" is reached)

- To visualise the application traversal graph the script **visualize_graph.py** can be run directly, without the need for WinAppDriver. Assuming the crawler has been run before and produced the pickled file *graphs* (comprised of two dicts) which is contained in the *./screens_temp* directory. Run:
```Python
python dfs_crawl.py
```
This will produce an .svg image of the graph. In this way the nodes and their states can be inspected visually.

- Similarly as the previous script, **bbox_graph.py** can be run separately and relies on the data stored in *./screens_temp*. This script goes through the traversal graph and filters the bounding boxes in order to get a cleaner result by eliminating elements that are partially obstructed or not visible on screen. It is sufficient to run:
```Python
python bbox_graph.py
```
The script will output images with cleaner bounding boxes (maybe also add new .xml files or some other way of saving). **bbox_graph.py** basically runs **gui_filter_bbox.py** over the whole application graph.  **gui_filter_bbox.py** can also be used separately by providing the screen to be inspected and the previous screen (nothing if Root is to inspected) as arguments, in this way only one screenshot is filtered instead of the whole graph.

## Limitations

There are some limitations with the current implementation. Firstly applications which use GTK or other frameworks don't provide access to all element metadata. For example GIMP only provides access to the window containing the application and not to the content inside the window, other application like Adobe Reader have several panes containing gui element metadata that can't be accessed. These limitations are inherently present since WinAppDriver is the backbone and only Win32 framework metadata can be extracted. <br>
Another limitation which is due to how some applications are designed is due to the fact that some applications open windows/panes within a new process or within a window/pane that is not contained within the main application. This could be overcome by opening WinAppDriver in Root mode, meaning that it is not affixed to a specific application or process, but to the entire Desktop. Although this solution comes with new issues, when dealing with the whole Desktop WinAppDriver needs to query every application that's open and this takes a lot longer and can lead to new complications (frequent crashes). Another issue arises in detecting which elements on the Desktop are linked to the application under test, since it is not discernible with a unique method that works on all applications. In some applications it might be impossible since there are no fixed naming conventions or there is no available information to link the windows and processes. 
