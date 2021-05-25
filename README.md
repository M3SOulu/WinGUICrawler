# GUI-Element-Identification

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

# Papers
Rico: A Mobile App Dataset for Building Data-Driven Design Applications
https://doi.org/10.1145/3126594.3126651

VINS: Visual Search for Mobile User Interface Design
https://doi.org/10.1145/3411764.3445762

pix2code: Generating Code from a Graphical User Interface Screenshot
https://arxiv.org/abs/1705.07962
