#from apiclient.discovery import build
import xml.etree.ElementTree as ET
import json
import sys
import os
import HTMLParser
from languageDatabase import langDatabase
stdin, stdout = sys.stdin, sys.stdout
reload(sys)
sys.stdin, sys.stdout = stdin, stdout
sys.setdefaultencoding('utf-8')
translator = langDatabase()
count = 0


# xcodebuild -importLocalizations -localizationPath <dirpath> -project <projectname> [-forceImport]

# xcodebuild -exportLocalizations -localizationPath <dirpath> -project <projectname> [[-exportLanguage <targetlanguage>]]


def translateText(text, target="en", source="en"):
    global count
    count += len(text)
    return translator.translate(text, target, source)


def translateFile(filename, path):
    #print filename, path
    tree = ET.parse(path+filename)
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
    for xliff in root:
        for file in xliff:
            if file.tag == "{urn:oasis:names:tc:xliff:document:1.2}body" or file.tag == "body":
                print "+",
                for body in file:
                    if body.tag == "{urn:oasis:names:tc:xliff:document:1.2}trans-unit" or body.tag == "trans-unit":
                        attrib = body.attrib
                        foundTarget = False
                        source = ""
                        target = ""
                        for item in body:
                            if item.tag == "{urn:oasis:names:tc:xliff:document:1.2}source" or item.tag == "source":
                                source = item #found the item, store it
                                print ".",
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
                                if source.text != new.text:
                                    body.append(new)
                            else:
                                # Never found it Add it in
                                new = ET.Element('{urn:oasis:names:tc:xliff:document:1.2}target')
                                translated = translateText(source.text, targetLang)
                                translatedEncoded = translated.encode('UTF-8')
                                new.text = parser.unescape(translatedEncoded)
                                #print new.text
                                if source.text != new.text:
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
                                if source.text != new.text:
                                    body.append(new)
                            else:
                                translated = translateText(source.text, targetLang)
                                translatedEncoded = translated.encode('UTF-8')
                                target.text = parser.unescape(translatedEncoded)
                                #print target.text

    print "#",
    tree.write(path+filename,encoding="UTF-8",xml_declaration=True)
    print "#",

    f = open(path+filename,'r')
    filedata = f.read().encode('utf-8')
    f.close()
    print "#",
    newdata = filedata.replace("ns0:","") # delete ns0: character in file
    print "#",
    f = open(path+filename,'w')
    f.write(newdata.encode('utf-8'))
    f.close()
    print "#"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Correct Usage: 'python localizeFile.py {FOLDER_TO_TRANSLATE}'")
    elif sys.argv[1] == "--rm-cache":
        if os.path.exists("cache.json"): #file exist
            os.remove("cache.json")
    else:
        path = sys.argv[1]+'/'

        for filename in os.listdir(path):
            translateFile(filename, path)
            print str(count)+" letters"
