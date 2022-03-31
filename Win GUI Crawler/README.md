# Win GUI Crawler

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependancies (assuming you have python3 installed).

```bash
pip install Appium-Python-Client==1.3.0
pip install pyautogui
pip install pywin32==225
pip install keyboard
pip install opencv-python
pip install psutil
pip install lxml
pip install win10toast
```
Install graphviz from https://graphviz.org/download/ or if using anaconda simly run
```bash
conda install python-graphviz
```
Install graphviz module for python
```bash
pip install graphviz
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
There are several scripts in this project. Let's go through each one and their usage.

- Taking screenshots by keypress is possible with **take_screen.py**, everything will be saved in the *./taken_screens* directory unless differently specified. Before running it, the desired Windows application needs to be specified under *desired_caps["app"]* (either by automation Id or exe location). To run mspaint for example:
```Python
desired_caps["app"] = r"C:\Windows\System32\mspaint.exe"
```
To run the scipt, firstly make sure to have WinAppDriver listening on port 4724 in the background, and then run:
```Python
python take_screen.py
```
After waiting for several seconds the prompt will ask for a keypress (a win10 toast notification will also be displayed), pressing "p" takes a screenshot and pressing "e" exits the script. After taking a screenshot wait for a for the prompt to ask for another keypress before taking another one.

- The crawler is implemented in **dfs_crawl.py**, similarly to the previous script, unless differently specified everything gets saved in the *./screens_temp* directory. Furthermore the same things apply with regards to WinAppDriver running in background and desired_caps["app"] being set to the desired application. <br> The crawler takes in an argument which is a non negative integer N, if N==0 the crawler keeps going until the whole application is explored, if N > 0 the crawler does N passes. Each pass will make the crawler go from Root to the end of a branch of the traversal graph.
After making sure everything is set, run the crawler:
```Python
python dfs_crawl.py 0 #the crawler runs until root dies and the application is fully explored
```
Or
```Python
python dfs_crawl.py 10 #the crawler runs 10 passes
```

 This script produces images, xml metadata and a graph which is saved as two dictionaries in the file *graphs*.

- To visualise the application traversal graph the script **visualize_graph.py** can be run directly, without the need for WinAppDriver. Assuming the crawler has been run before and produced the pickled file *graphs* (comprised of two dicts) which is contained in the specified directory. The script takes the name of the directory containing the data produced by the crawler as an argument (e.g. *screens_temp*).

 Run:
```Python
python dfs_crawl.py screens_temp
```
This will produce an .svg image of the graph. Making it possible for the nodes and their states to be inspected visually.

- Similarly as the previous script, **bbox_graph.py** can be run separately and relies on the data stored in the specified directory (e.g. *screens_temp*). The directory name is passed as an argument.
 This script goes through the traversal graph and filters the bounding boxes in order to get a cleaner result by eliminating elements that are partially obstructed or not visible on screen, saving the metadata with relevant tags in json format. Additionally it saves cropped images of all the gui elements and writes the metadata for each element in csv format.

 It is sufficient to run:
```Python
python bbox_graph.py screens_temp
```
The script will output images with cleaner bounding boxes. **bbox_graph.py** basically runs **gui_filter_bbox.py** over the whole application graph.  **gui_filter_bbox.py** can also be used separately by providing the screen to be inspected and the previous screen (nothing if Root is to be inspected) as arguments, in this way only one screenshot is filtered instead of the whole graph. <br> The script can also be run over data that wasn't obtained from crawling the application (data obtained with **take_screen.py**).
