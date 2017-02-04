import xml.etree.ElementTree as ET
import os
import html.parser as htmlparser

# store past translations in an XML file, and a separate lookup for human entries

'''
<source text="">
    <translation lang=""> text
'''


class langDatabase():
    preferredTree = ""
    lookupTree = ""
    
    def __init__(self):
        #Load the files
        lookup_path = "lookup.xml"
        preferred_path = "preferred.xml"
        if os.path.exists(lookup_path): #file exist
            lookupTree = ET.parse(lookup_path)
        
        
        else: #create a new file
            
            root = ET.Element("root")
            doc = ET.SubElement(root, "doc")

            ET.SubElement(doc, "field1", name="blah").text = "some value1"
            ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"

            lookupTree = ET.ElementTree(root)
            lookupTree.write(lookup_path)

    def add(source, translated, lang):
        #check if source is already in the tree
            #if it is, replace it
            #if not, add it
    
    def translate(source, target, source="en"):
        #check if source is already in the preferred tree
            #if it is, return that
            #if it isn't, check if it's in the lookup list
                #if it is, return that
                #last resort, use google translate, store result
                    #check if it's a valid language, otherwise return original

    def __del__(self):
        # save the tree, if it changed
        lookupTree.write(lookup_path)
        preferredTree.write(preferred_path)
