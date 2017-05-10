import json
import os
from translate import GoogleTranslator


# store past translations in an XML file, and a separate lookup for human entries

'''
<source text="">
    <translation lang=""> text
'''

def writeJSON(fileName, data):
    with open(fileName, 'w') as outfile:
        json.dump(data, outfile)

def readJSON(fileName):
    with open(fileName) as data_file:
        return json.load(data_file)


class langDatabase():
    preferredTree = {}
    lookupTree = {}
    
    def __init__(self):
        #Load the files
        lookup_path = "cache.json"
        preferred_path = "preferred.json"
        if os.path.exists(lookup_path): #file exist
            self.lookupTree = readJSON(lookup_path)
        
        if os.path.exists(preferred_path):
            self.preferred_path = readJSON(preferred_path)

        # File will be automatically created otherwise
        
        assert(os.path.exists("config.json"))
        json = readJSON("config.json")
        assert("api" in json)
        assert("google_translate" in json["api"])
        api = json["api"]["google_translate"]
        assert(api != "YOUR_API_KEY_HERE")
        
        self.translator = GoogleTranslator(api)

    def add(self, original, translated, target, source):
        if source not in self.lookupTree:
            self.lookupTree[source] = {}
        
        if target not in self.lookupTree[source]:
            self.lookupTree[source][target] = {}
        
        if original not in self.lookupTree[source][target]:
            self.lookupTree[source][target][original] = translated
    
    def translate(self, original, target, source="en"):
        #check if source is already in the preferred tree
        trees = [self.preferredTree, self.lookupTree]
        
        for tree in trees:
            if source in tree:
                if target in tree[source]:
                    if original in tree[source][target]:
                        return tree[source][target][original]

        # Must not be cached
        trans = self.translator.translate(original, source, target) # always translating from english
        add(original, trans, target, source)
    
        return trans


    def __del__(self):
        # save the tree, if it changed
        lookup_path = "cache.json"
        preferred_path = "preferred.json"
        writeJSON(lookup_path, self.lookupTree)
        writeJSON(preferred_path, self.preferredTree)
