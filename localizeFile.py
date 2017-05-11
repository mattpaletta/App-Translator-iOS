#from apiclient.discovery import build
import xml.etree.ElementTree as ET
import json
import sys
import re
import os
import HTMLParser
from languageDatabase import langDatabase
stdin, stdout = sys.stdin, sys.stdout
reload(sys)
sys.stdin, sys.stdout = stdin, stdout
sys.setdefaultencoding('utf-8')
translator = None
count = 0


# xcodebuild -importLocalizations -localizationPath <dirpath> -project <projectname> [-forceImport]

# xcodebuild -exportLocalizations -localizationPath <dirpath> -project <projectname> [[-exportLanguage <targetlanguage>]]


def translateText(text, target="en", source="en"):
    global count
    global translator
    
    count += len(text.split(" "))
    
    # if incorrect tree loaded, reload the correct tree
    if translator is None:
        translator = langDatabase(source, target)
    elif translator.source != source or translator.target != target:
        translator = langDatabase(source, target)
    
    paragraph = text.split(".")
    output = []
    for txt in paragraph:
        output.append(translator.translate(txt, target, source))
    return '.'.join(output)


def translateFile(filename, path):
    
    inputFile = os.path.join(path, filename)
    
    #print filename, path
    print(inputFile)
    #ET.register_namespace('', "urn:oasis:names:tc:xliff:document:1.2")
    #ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    #ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    #ET.register_namespace('schemaLocation', "urn:oasis:names:tc:xliff:document:1.2 http://docs.oasis-open.org/xliff/v1.2/os/xliff-core-1.2-strict.xsd")
    
    tree = ET.parse(inputFile)
    root = tree.getroot()

    parser = HTMLParser.HTMLParser()

    #root->file->body->trans-unit (source, target, note)
    #print root.tag
    data = filename.split(".")
    targetLang = data[0]
    if targetLang == "es-MX":
        targetLang = "es"
    if targetLang == "he":
        targetLang = "iw"
    if targetLang == "nb":
        targetLang = "no"
    if targetLang == "pt-BR":
        targetLang = "pt"
    if targetLang == "pt-PT":
        targetLang = "pt"
    if targetLang == "pt-PT":
        targetLang = "pt"
    if targetLang == "zh-Hans":
        targetLang = "zh-CN"
    if targetLang == "zh-Hant":
        targetLang = "zh-TW"


    print "Translating "+targetLang
    p = re.compile("[0-9]+.*[0.9]* | \$\w*")

    for xliff in root:
        #print(xliff)
        for file in xliff:
            #print(file)
            if file.tag == "{urn:oasis:names:tc:xliff:document:1.2}body" or file.tag == "body":
                #print "+",
                for body in file:
                    #print(body)
                    if body.tag == "{urn:oasis:names:tc:xliff:document:1.2}trans-unit" or body.tag == "trans-unit":
                        attrib = body.attrib
                        foundTarget = False
                        source = ""
                        target = ""
                        for item in body:
                            if item.tag == "{urn:oasis:names:tc:xliff:document:1.2}source" or item.tag == "source":
                                source = item #found the item, store it
                                print "*",
                            if item.tag == "{urn:oasis:names:tc:xliff:document:1.2}target" or item.tag == "target":
                                target = item #found the item, store it
                                foundTarget = True
                                print ".",
                            
                        if foundTarget == False:
                            if attrib["id"] == 'CFBundleName' or attrib["id"] == 'CFBundleShortVersionString':
                                # Never found it Add it in
                                new = ET.Element('{urn:oasis:names:tc:xliff:document:1.2}target')
                                raw = source.text
                                translatedEncoded = raw.encode('UTF-8')
                                new.text = parser.unescape(translatedEncoded)
                                #print new.text
                                if source.text != new.text or p.search(source.text) is None:
                                    #print(new.text)
                                    body.append(new)
                            else:
                                # Never found it Add it in
                                new = ET.Element('{urn:oasis:names:tc:xliff:document:1.2}target')
                                translated = translateText(source.text, targetLang)
                                translatedEncoded = translated.encode('UTF-8')
                                new.text = parser.unescape(translatedEncoded)
                                #print(new.text)
                                if source.text != new.text or p.search(source.text) is None:
                                    #print(new.text)
                                    body.append(new)
                        # Update it from Google or from Human Dictionary
                        else:
                            if attrib["id"] == 'CFBundleName' or attrib["id"] == 'CFBundleShortVersionString':
                                # Never found it Add it in
                                new = ET.Element('{urn:oasis:names:tc:xliff:document:1.2}target')
                                raw = source.text
                                translatedEncoded = raw.encode('UTF-8')
                                target.text = parser.unescape(translatedEncoded)
                                #print new.text
                                if source.text != new.text or p.search(source.text) is None:
                                    #print(new.text)
                                    body.append(new)
                            else:
                                translated = translateText(source.text, targetLang)
                                translatedEncoded = translated.encode('UTF-8')
                                target.text = parser.unescape(translatedEncoded)
                                #print target.text
                                        
    print "#",
    tree.write(str(inputFile), encoding="UTF-8",xml_declaration=True)
    print "#",
    f = open(str(inputFile),'r')
    filedata = f.read().encode('utf-8')
    f.close()
    print "#",
    newdata = filedata.replace("ns0:","") # delete ns0: character in file
    newdata = newdata.replace("ns1:","") # delete ns0: character in file
    print "#",
    f = open(str(inputFile),'w')
    f.write(newdata.encode('utf-8'))
    f.close()
    print "#"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Correct Usage: 'python localizeFile.py {FOLDER_TO_TRANSLATE}'")
        exit()
    if len(sys.argv) > 1 and sys.argv[1] == "--rm-cache":
        if os.path.exists("cache/"): #file exist
            os.system("rm -r cache")

    if sys.argv[1] == "/":
        path = '.'
    else:
        path = sys.argv[1]

    auto = False

    # Set default langs in case not specified in JSON Config
    langs = ["ar", "ca", "cs", "da", "de", "el", "es-419", "es-MX", "es", "fi", "fr", "he", "hr", "hu", "id", "it", "ja", "ko", "ms", "nb", "nl", "pl", "pt-BR", "pt-PT", "ro", "ru", "sk", "sv", "th", "tr", "uk", "vi", "zh-Hans", "zh-Hant"]

    if len(sys.argv) > 2 and sys.argv[2] == "--auto":
        print("auto")
        auto = True
        projectBase = None
        for root, subFolders, files in os.walk(path):
            if root.endswith('.xcodeproj') and os.path.islink(root) == False and "project.xcworkspace" in subFolders:
                # remember location of base
                projectBase = root
                print(root, subFolders)

        exports = " -exportLanguage ".join(langs)
        projectName = projectBase.split("/")[1]
        print(projectName)

        print("xcodebuild -exportLocalizations -localizationPath ./"+projectName+" -project "+str(projectBase) + " -exportLanguage " + str(exports))
        os.system("xcodebuild -exportLocalizations -localizationPath ./"+projectName+" -project "+str(projectBase) + " -exportLanguage " + str(exports))

        path = projectName+"/"

    for root, subFolders, files in os.walk(path):
        for file in files:
            if file.endswith('.xliff') and os.path.islink(os.path.join(root, file)) == False:
                print(os.path.join(root, file))
                translateFile(file, root)
            elif (file.endswith('.ai') or file.endswith('.psd')) and os.path.islink(os.path.join(root, file)) == False:
                print(file)
                print("Found Image! Translating...")

    if auto:
        print("auto")
        
        exports = " -exportLanguage ".join(langs)
        projectName = projectBase.split("/")[1]
        print(projectName)
        
        for lang in langs:
            # import one at a time
            print("xcodebuild -importLocalizations -localizationPath ShopEasy/"+lang+".xliff -project "+projectBase)
            os.system("xcodebuild -importLocalizations -localizationPath ShopEasy/"+lang+".xliff -project "+projectBase)
        
        path = projectName+"/"


    print str(count)+" words"
