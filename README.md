# Win GUI Crawler

Maybe I can write a shorter version and add methods to the other readme....

## Intro

This tool was developed in order to compile a large-scale gui image/metadata database with the purpose of using this database to improve gui elements identification with machine learning methods. Existing databases only concern mobile and web gui's, there is no large-scale database in the Desktop domain. In order to fill that gap a crawler was developed that automatically traverses a Windows Desktop application (using Win32 API) and collects screenshots with relative metadata. </br>
The backbone of this tool is based on [WinAppDriver](https://github.com/microsoft/WinAppDriver), which is a service to support Selenium-like UI Test Automation on Windows Applications.  



## Features and Methods

The Win GUI Crawler has several features and the methods it employs will be briefly explained in this section.

# Crawling

As its name implies, the main objective of this tool is to automatically traverse a Windows application and collect image screenshots and related metadata. Crawlers are usually employed to extract data from websites and can take a depth first or breadth first approach, for Windows applications depth first search is more appropriate since traversal happens only in one direction (it is not always possible to go back to the previous screen). The crawler will create a tree structure where traversal will be recorded. In this tree nodes correspond to gui screens and edges correspond to actions that can take the application from one screen to another. Actions will correspond to clicking certain gui elements. To reduce the problem space and to make the traversal manageable new edges will be associated to newly found actions. For example, if the crawler is at screen A and can press buttons A1,A2,A3, let's say it presses A1 which takes it to screen B where the possible actions are A2,A3,B1,B2 the crawler will ignore A2,A3 since these two actions are already present in the previous screen and will thus only consider the new actions. In this way the complexity is reduced and excessive redundancy is avoided. A node will die when it doesn't produce new actions or when all it's children die. The application is fully explored when the root node is dead, meaning all nodes are dead. The crawler only takes screenshot at nodes which produce new actions meaning that they have new content, again to avoid excessive redundancy. Since there is no tag in the metadata that uniquely identifies gui elements, they are uniquely identified by an xpath generated from the xml metadata tree.

# Filtering

# Possible uses

## Limitations

There are several limitations with the current implementation. Firstly, applications which use GTK or other frameworks don't provide access to all element metadata. For example GIMP only provides access to the window containing the application and not to the content inside the window, other application like Adobe Reader have several panes containing gui element metadata that can't be accessed. These limitations are inherently present since WinAppDriver is the backbone and only Win32 framework metadata can be extracted. <br>
Another limitation is due to the fact that some applications open windows/panes within a new process or within a window/pane that is not contained within the main application window. This could be fixed by opening WinAppDriver in Root mode, meaning that it is not affixed to a specific application or process, but to the entire Desktop. However, this solution comes with new issues, when dealing with the whole Desktop WinAppDriver needs to query every application that's open and this takes a lot longer and can lead to frequent crashes. Another issue arises in detecting which elements on the Desktop are linked to the application under test, since it is not discernible with a unique method that works on all applications. In some applications it might be impossible since there are no fixed naming conventions or there is no available information to link the windows and processes.
