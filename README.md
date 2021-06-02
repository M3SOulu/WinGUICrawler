# GUI-Element-Identification

Name | Link | Paper | Maturity | Domain | Data Collection Method | Summary | Open Questions
---- | ---- | ----- | -------- | ------ | ---------------------- | ------- | --------------
RFW-Eficode | https://github.com/eficode/robotframework-imagehorizonlibrary | NA | 3 |Robot-Framework /  Web? | ? | Project seems active | Where is the image data?
OpenUIdataset | https://github.com/openuidata/openuidataset | NA | ? | Any UI displayed on Win10 | Automated GUI exploration using Testar Tool to get screenshots and widget data | An idea on how to collect GUI screenshots | How well does it work? What widget data can it collect? 

# Data / Libraries

Eficode image horizon library
Summary: Seem active. I do not see any data here. 
https://github.com/eficode/robotframework-imagehorizonlibrary

Open UI Data set. 
Summary: An idea on how to collect GUI screenshots. 
https://github.com/openuidata/openuidataset

Rico
Summary: Large scale mobile app dataset with semantic annotations and recorded interactions. Crowdsourced and automated exploring. Labeling seems to be done manually, "we annotate elements with any Android superclasses that they are derived from", unclear if also via crowdsourcing or they did it locally.
https://interactionmining.org/rico

VINS
Summary: Smaller dataset than Rico, but they state that they provide better labeling and content hierarcy. They crowdsourced the annotation process and it's nicely explained, good tips if we need to annotate via crowdsourcing.
https://github.com/sbunian/VINS

Pix2code 
Summary: Small dataset with mobile and web-based ui 
synthetic data, so probably not a great idea, but a good intuiton about web-based apps.
Theoretically we could implement an automated method to extract web-based app ui images and also labeled bounding boxes (if web-based app data is useful in practice).
https://github.com/tonybeltramelli/pix2code

ReDraw
Summary: Similar project to pix2code, mobile user interface data. They constuct a dataset by mining screenshots and metadata (extracted using UI-frameworks) to automatically obtain labeled images. 
https://zenodo.org/record/2530277#.YLSu0iZRVNg

iOS app screen dataset:
Summary: UI element detection on iOS. Firstly they collect screenshots and metadata by having workers manually traverse apps. Subsequently the workers annotate the images in two steps: segmentation and classification. Fairly straightforward labeling, first they draw bounding boxes and then put them in categories.

CSS frameworks dataset:
Summary: Small dataset for web-based gui recognition. Images of cropped gui elements taken from CSS framework example pages.
https://github.com/agylardi/guicore-alpha

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

