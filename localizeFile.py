#from apiclient.discovery import build
from translate import GoogleTranslator
import xml.etree.ElementTree as ET
import json
import sys
import os
import html.parser as htmlparser
stdin, stdout = sys.stdin, sys.stdout
reload(sys)
sys.stdin, sys.stdout = stdin, stdout
sys.setdefaultencoding('utf-8')
translator = GoogleTranslator()
count = 0

def translateText(text, target="en"):
    global count
    count += len(text)
    return text
    '''translation = translator.translate(text, "en", target) # always translating from english
    print translation
    return translation'''

def translateFile(filename, path):
    #print filename, path
    tree = ET.parse(path+filename)
    root = tree.getroot()

    parser = htmlparser.HTMLParser()

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
                                body.append(new)
                            else:
                                # Never found it Add it in
                                new = ET.Element('{urn:oasis:names:tc:xliff:document:1.2}target')
                                translated = translateText(source.text, targetLang)
                                translatedEncoded = translated.encode('UTF-8')
                                new.text = parser.unescape(translatedEncoded)
                                #print new.text
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
path = 'Pigmentum/'

for filename in os.listdir(path):
    # do your stuff
    translateFile(filename, path)

print str(count)+" letter"