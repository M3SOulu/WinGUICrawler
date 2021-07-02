# GUI-Element-Identification

## Data Collection Methods/Papers

Name | Paper | Domain | Data Collection Method | Summary | Open Questions
---- | ----- | ------ | ---------------------- | ------- | --------------
[Robocorp](https://github.com/robocorp/rpaframework/tree/master/packages/recognition)| [Doc1](https://robocorp.com/docs/developer-tools/robocorp-lab/locating-and-targeting-UI-elements) [Doc-Web](https://robocorp.com/docs/development-guide/browser/how-to-find-user-interface-elements-using-locators-in-web-applications) [Doc-Win10](https://robocorp.com/docs/development-guide/desktop/how-to-find-user-interface-elements-using-locators-and-keyboard-shortcuts-in-windows-applications) | ? | Robot-Framework|?|?
[RFW-Eficode](https://github.com/eficode/robotframework-imagehorizonlibrary) | NA |Robot-Framework /  Web? | ? | Project seems active | Where is the image data?
[OpenUIdataset](https://github.com/openuidata/openuidataset) | NA | Any Win10 UI | Automated exploration with tool | Idea on GUI screenshots collection | Working? Collects what widget data?
[Rico](https://interactionmining.org/rico) | https://doi.org/10.1145/3126594.3126651 | Android | Crowdsourced and automated exploring, labeling unclear | Large dataset with semantic annotations and recorded interactions | How did they label the images?   
[VINS](https://github.com/sbunian/VINS) | https://doi.org/10.1145/3411764.3445762 | Android and iOS |Screenshots from Rico and collected manually, crowdsourced labeling | Smaller than Rico, better labeling and content hierarcy. | ? 
[Pix2code](https://github.com/tonybeltramelli/pix2code) | https://arxiv.org/abs/1705.07962 | Android, iOS and Web | Synthetic data created via UI generator | transform images into layout code, good intuition on web apps | How useful is synthetic data?
[ReDraw](https://zenodo.org/record/2530277#.YLSu0iZRVNg) | https://arxiv.org/abs/1802.02312 | Android | mined screenshots and metadata (using uiautomate) | Similar project to pix2code, automatic labeling with extracted metadata | ?
iOS screen | https://arxiv.org/abs/2101.04893 | iOS | Workers collect screenshots, then segment and classify | UI element detection on iOS, straightforward labeling | ?
[CSS frameworks](https://github.com/agylardi/guicore-alpha) | http://dx:doi:org/10:21609/jiki:v13i1:845 | Web | Manually cropped element images taken from CSS example pages | Small dataset for web gui recognition | ?
[WinAppDriver](https://github.com/Microsoft/WinAppDriver)| ... | Windows | ... | Selenium-like UI Test Automation on Windows Applications, developed by Microsoft | Project dead?    
[UI Image to GUI Skeleton](http://tagreorder.appspot.com/ui2code.html) |  https://chunyang-chen.github.io/publication/ui2code.pdf | Android | Automated exploration of apps | Exploration actions assigned dynamic weights, removed duplicates by comparing gui code hashes | ...

## Algorithmic Papers

Name | Paper | Domain | Data Collection Method | Summary | Open Questions
---- | ----- | ------ | ---------------------- | ------- | --------------
DL vs. Old | https://arxiv.org/pdf/2008.05132.pdf | Android| None use Rico | Combination of DL and old works best| ? |
Mobile Semantics | https://dl.acm.org/doi/10.1145/3242587.3242650 | Android | Rico, reclassified according to lexical database | Deeper classification of ui elements ( 25 UI component categories, 197 text button concepts, and 99 classes of icons), UI components and text buttons code-based classification and icons with a CNN | ...

# Data / Libraries

Eficode image horizon library:\
Seem active. I do not see any data here. 
https://github.com/eficode/robotframework-imagehorizonlibrary

Open UI Data set:\
An idea on how to collect GUI screenshots. 
https://github.com/openuidata/openuidataset

Rico:\
Large scale mobile app dataset with semantic annotations and recorded interactions. Crowdsourced and automated exploring. Labeling seems to be done manually, "we annotate elements with any Android superclasses that they are derived from", unclear if also via crowdsourcing or they did it locally.
https://interactionmining.org/rico

VINS:\
Smaller dataset than Rico, but they state that they provide better labeling and content hierarcy. They crowdsourced the annotation process and it's nicely explained, good tips if we need to annotate via crowdsourcing. 
https://github.com/sbunian/VINS

Pix2code:\
Small dataset with mobile and web-based ui 
synthetic data, so probably not a great idea, but a good intuiton about web-based apps.
Theoretically we could implement an automated method to extract web-based app ui images and also labeled bounding boxes (if web-based app data is useful in practice).
https://github.com/tonybeltramelli/pix2code

ReDraw:\
Similar project to pix2code, mobile user interface data. They constuct a dataset by mining screenshots and metadata (extracted using UI-frameworks) to automatically obtain labeled images. 
https://zenodo.org/record/2530277#.YLSu0iZRVNg

iOS app screen dataset:\
UI element detection on iOS. Firstly they collect screenshots and metadata by having workers manually traverse apps. Subsequently the workers annotate the images in two steps: segmentation and classification. Fairly straightforward labeling, first they draw bounding boxes and then put them in categories.

CSS frameworks dataset:\
Small dataset for web-based gui recognition. Images of cropped gui elements taken from CSS framework example pages.
https://github.com/agylardi/guicore-alpha

WinAppDriver:\
Test automation tool developed by Microsoft (seems either dead or on hiatus), best alternative for collecting data on windows and most isssues can be resolved with community workarounds
https://github.com/Microsoft/WinAppDriver

UI Image to GUI Skeleton:\
Neureal Network approach to translate Android UI images to GUI skeletons, the network is trained on data collected via a GUI exploration tool. The exploration tool prioritizes actions to execute based on dynamic weights, duplicate images are found by comparing hashes of underlying ui design code.
https://chunyang-chen.github.io/publication/ui2code.pdf

# Papers
Rico: A Mobile App Dataset for Building Data-Driven Design Applications
https://doi.org/10.1145/3126594.3126651

VINS: Visual Search for Mobile User Interface Design
https://doi.org/10.1145/3411764.3445762

pix2code: Generating Code from a Graphical User Interface Screenshot
https://arxiv.org/abs/1705.07962

ReDraw: Machine Learning-Based Prototyping of Graphical User Interfaces for Mobile Apps
https://arxiv.org/abs/1802.02312

iOS app screen dataset: Screen Recognition - Creating Accessibility Metadata for Mobile Applications from Pixels
https://arxiv.org/abs/2101.04893

CSS frameworks dataset: Visual Recognition of Graphical User Interface Components using Deep Learning Technique
http://dx:doi:org/10:21609/jiki:v13i1:845

Object Detection for Graphical User Interface: Old Fashioned orDeep Learning or a Combination?
https://arxiv.org/pdf/2008.05132.pdf

Learning Design Semantics for Mobile Apps
https://dl.acm.org/doi/10.1145/3242587.3242650

From UI Design Image to GUI Skeleton: A Neural Machine Translator to Bootstrap Mobile GUI Implementation
https://chunyang-chen.github.io/publication/ui2code.pdf
