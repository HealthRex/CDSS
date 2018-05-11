import sys,os;
import urllib;
from xml.etree import ElementTree;

tree = ElementTree.parse(sys.argv[1]);

for abstract in tree.iter("Abstract"):
    comboTextList = list();
    for abstractText in abstract.iter("AbstractText"):
        if abstractText.text is not None:
            comboTextList.append(abstractText.text);
    comboText = str.join("    ", comboTextList );
    print comboText.encode("unicode-escape");
