# Win GUI Crawler

## Intro

This tool was developed in order to compile a large-scale gui image/metadata database with the purpose of using this database to improve gui elements identification with machine learning methods. Existing databases only concern mobile and web gui's, there is no large-scale database in the Desktop domain. In order to fill that gap a crawler was developed that automatically traverses a Windows Desktop application (using Win32 API) and collects screenshots with relative metadata. </br>
The backbone of this tool is based on [WinAppDriver](https://github.com/microsoft/WinAppDriver), which is a service to support Selenium-like UI Test Automation on Windows Applications.  



## General information


## Limitations

There are several limitations with the current implementation. Firstly, applications which use GTK or other frameworks don't provide access to all element metadata. For example GIMP only provides access to the window containing the application and not to the content inside the window, other application like Adobe Reader have several panes containing gui element metadata that can't be accessed. These limitations are inherently present since WinAppDriver is the backbone and only Win32 framework metadata can be extracted. <br>
Another limitation is due to the fact that some applications open windows/panes within a new process or within a window/pane that is not contained within the main application window. This could be fixed by opening WinAppDriver in Root mode, meaning that it is not affixed to a specific application or process, but to the entire Desktop. However, this solution comes with new issues, when dealing with the whole Desktop WinAppDriver needs to query every application that's open and this takes a lot longer and can lead to frequent crashes. Another issue arises in detecting which elements on the Desktop are linked to the application under test, since it is not discernible with a unique method that works on all applications. In some applications it might be impossible since there are no fixed naming conventions or there is no available information to link the windows and processes.
