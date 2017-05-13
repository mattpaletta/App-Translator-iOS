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
estimate = None
count = 0


# xcodebuild -importLocalizations -localizationPath <dirpath> -project <projectname> [-forceImport]

# xcodebuild -exportLocalizations -localizationPath <dirpath> -project <projectname> [[-exportLanguage <targetlanguage>]]


def translateText(text, target="en", source="en"):
    global count
    global translator
    global estimate
    
    count += len(text)
    
    # if incorrect tree loaded, reload the correct tree
    if translator is None:
        translator = langDatabase(source, target)
    elif translator.source != source or translator.target != target:
        translator = langDatabase(source, target)
    
    paragraph = text.split(".")
    output = []
    sum = 0
    for txt in paragraph:
        if estimate is None:
            output.append(translator.translate(txt, target, source))
        else:
            sum += translator.estimate(txt, target, source)
    
    if estimate is None:
        return '.'.join(output)
    else:
        return sum

def translateFile(filename, path):
    global estimate
    
    inputFile = os.path.join(path, filename)
    
    #print filename, path
    #print(inputFile)
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
                                if estimate is not None:
                                    estimate += translateText(source.text, targetLang)
                                else:
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
                                if estimate is not None:
                                    estimate += translateText(source.text, targetLang)
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

    if len(sys.argv) > 1 and sys.argv[2] == "--estimate":
        estimate = 0

    if sys.argv[1] == "/":
        path = '.'
    else:
        path = sys.argv[1]

    auto = False

    # Set default langs in case not specified in JSON Config
    langs = ['af', 'af-NA', 'af-ZA', 'agq', 'agq-CM', 'ak', 'ak-GH', 'am', 'am-ET', 'ar', 'ar-001', 'ar-AE', 'ar-BH', 'ar-DJ', 'ar-DZ', 'ar-EG', 'ar-EH', 'ar-ER', 'ar-IL', 'ar-IQ', 'ar-JO', 'ar-KM', 'ar-KW', 'ar-LB', 'ar-LY', 'ar-MA', 'ar-MR', 'ar-OM', 'ar-PS', 'ar-QA', 'ar-SA', 'ar-SD', 'ar-SO', 'ar-SS', 'ar-SY', 'ar-TD', 'ar-TN', 'ar-YE', 'ars', 'as', 'as-IN', 'asa', 'asa-TZ', 'ast', 'ast-ES', 'az', 'az-AZ', 'az-Cyrl', 'az-Cyrl-AZ', 'bas', 'bas-CM', 'be', 'be-BY', 'bem', 'bem-ZM', 'bez', 'bez-TZ', 'bg', 'bg-BG', 'bm', 'bm-ML', 'bn', 'bn-BD', 'bn-IN', 'bo', 'bo-CN', 'bo-IN', 'br', 'br-FR', 'brx', 'brx-IN', 'bs', 'bs-BA', 'bs-Cyrl', 'bs-Cyrl-BA', 'ca', 'ca-AD', 'ca-ES', 'ca-FR', 'ca-IT', 'ce', 'ce-RU', 'cgg', 'cgg-UG', 'chr', 'chr-US', 'ckb', 'ckb-IQ', 'ckb-IR', 'cs', 'cs-CZ', 'cy', 'cy-GB', 'da', 'da-DK', 'da-GL', 'dav', 'dav-KE', 'de', 'de-AT', 'de-BE', 'de-CH', 'de-DE', 'de-LI', 'de-LU', 'dje', 'dje-NE', 'dsb', 'dsb-DE', 'dua', 'dua-CM', 'dyo', 'dyo-SN', 'dz', 'dz-BT', 'ebu', 'ebu-KE', 'ee', 'ee-GH', 'ee-TG', 'el', 'el-CY', 'el-GR', 'en-001', 'en-150', 'en-AD', 'en-AG', 'en-AI', 'en-AL', 'en-AS', 'en-AT', 'en-AU', 'en-BA', 'en-BB', 'en-BE', 'en-BI', 'en-BM', 'en-BR', 'en-BS', 'en-BW', 'en-BZ', 'en-CA', 'en-CC', 'en-CH', 'en-CK', 'en-CM', 'en-CN', 'en-CX', 'en-CY', 'en-CZ', 'en-DE', 'en-DG', 'en-DK', 'en-DM', 'en-EE', 'en-ER', 'en-ES', 'en-FI', 'en-FJ', 'en-FK', 'en-FM', 'en-FR', 'en-GB', 'en-GD', 'en-GG', 'en-GH', 'en-GI', 'en-GM', 'en-GR', 'en-GU', 'en-GY', 'en-HK', 'en-HR', 'en-HU', 'en-IE', 'en-IL', 'en-IM', 'en-IN', 'en-IO', 'en-IS', 'en-IT', 'en-JE', 'en-JM', 'en-JP', 'en-KE', 'en-KI', 'en-KN', 'en-KR', 'en-KY', 'en-LC', 'en-LR', 'en-LS', 'en-LT', 'en-LU', 'en-LV', 'en-ME', 'en-MG', 'en-MH', 'en-MO', 'en-MP', 'en-MS', 'en-MT', 'en-MU', 'en-MV', 'en-MW', 'en-MY', 'en-NA', 'en-NF', 'en-NG', 'en-NL', 'en-NO', 'en-NR', 'en-NU', 'en-NZ', 'en-PG', 'en-PH', 'en-PK', 'en-PL', 'en-PN', 'en-PR', 'en-PT', 'en-PW', 'en-RO', 'en-RU', 'en-RW', 'en-SB', 'en-SC', 'en-SD', 'en-SE', 'en-SG', 'en-SH', 'en-SI', 'en-SK', 'en-SL', 'en-SS', 'en-SX', 'en-SZ', 'en-TC', 'en-TK', 'en-TO', 'en-TR', 'en-TT', 'en-TV', 'en-TW', 'en-TZ', 'en-UG', 'en-UM', 'en-US', 'en-US-POSIX', 'en-VC', 'en-VG', 'en-VI', 'en-VU', 'en-WS', 'en-ZA', 'en-ZM', 'en-ZW', 'eo', 'es', 'es-419', 'es-AR', 'es-BO', 'es-BZ', 'es-CL', 'es-CO', 'es-CR', 'es-CU', 'es-DO', 'es-EA', 'es-EC', 'es-ES', 'es-GQ', 'es-GT', 'es-HN', 'es-IC', 'es-MX', 'es-NI', 'es-PA', 'es-PE', 'es-PH', 'es-PR', 'es-PY', 'es-SV', 'es-US', 'es-UY', 'es-VE', 'et', 'et-EE', 'eu', 'eu-ES', 'ewo', 'ewo-CM', 'fa', 'fa-AF', 'fa-IR', 'ff', 'ff-CM', 'ff-GN', 'ff-MR', 'ff-SN', 'fi', 'fi-FI', 'fil', 'fil-PH', 'fo', 'fo-DK', 'fo-FO', 'fr', 'fr-BE', 'fr-BF', 'fr-BI', 'fr-BJ', 'fr-BL', 'fr-CA', 'fr-CD', 'fr-CF', 'fr-CG', 'fr-CH', 'fr-CI', 'fr-CM', 'fr-DJ', 'fr-DZ', 'fr-FR', 'fr-GA', 'fr-GF', 'fr-GN', 'fr-GP', 'fr-GQ', 'fr-HT', 'fr-KM', 'fr-LU', 'fr-MA', 'fr-MC', 'fr-MF', 'fr-MG', 'fr-ML', 'fr-MQ', 'fr-MR', 'fr-MU', 'fr-NC', 'fr-NE', 'fr-PF', 'fr-PM', 'fr-RE', 'fr-RW', 'fr-SC', 'fr-SN', 'fr-SY', 'fr-TD', 'fr-TG', 'fr-TN', 'fr-VU', 'fr-WF', 'fr-YT', 'fur', 'fur-IT', 'fy', 'fy-NL', 'ga', 'ga-IE', 'gd', 'gd-GB', 'gl', 'gl-ES', 'gsw', 'gsw-CH', 'gsw-FR', 'gsw-LI', 'gu', 'gu-IN', 'guz', 'guz-KE', 'gv', 'gv-IM', 'ha', 'ha-GH', 'ha-NE', 'ha-NG', 'haw', 'haw-US', 'he', 'he-IL', 'hi', 'hi-IN', 'hr', 'hr-BA', 'hr-HR', 'hsb', 'hsb-DE', 'hu', 'hu-HU', 'hy', 'hy-AM', 'id', 'id-ID', 'ig', 'ig-NG', 'ii', 'ii-CN', 'is', 'is-IS', 'it', 'it-CH', 'it-IT', 'it-SM', 'iu', 'iu-CA', 'ja', 'ja-JP', 'jgo', 'jgo-CM', 'jmc', 'jmc-TZ', 'ka', 'ka-GE', 'kab', 'kab-DZ', 'kam', 'kam-KE', 'kde', 'kde-TZ', 'kea', 'kea-CV', 'khq', 'khq-ML', 'ki', 'ki-KE', 'kk', 'kk-KZ', 'kkj', 'kkj-CM', 'kl', 'kl-GL', 'kln', 'kln-KE', 'km', 'km-KH', 'kn', 'kn-IN', 'ko', 'ko-KP', 'ko-KR', 'kok', 'kok-IN', 'ks', 'ks-IN', 'ksb', 'ksb-TZ', 'ksf', 'ksf-CM', 'ksh', 'ksh-DE', 'kw', 'kw-GB', 'ky', 'ky-KG', 'lag', 'lag-TZ', 'lb', 'lb-LU', 'lg', 'lg-UG', 'lkt', 'lkt-US', 'ln', 'ln-AO', 'ln-CD', 'ln-CF', 'ln-CG', 'lo', 'lo-LA', 'lrc', 'lrc-IQ', 'lrc-IR', 'lt', 'lt-LT', 'lu', 'lu-CD', 'luo', 'luo-KE', 'luy', 'luy-KE', 'lv', 'lv-LV', 'mas', 'mas-KE', 'mas-TZ', 'mer', 'mer-KE', 'mfe', 'mfe-MU', 'mg', 'mg-MG', 'mgh', 'mgh-MZ', 'mgo', 'mgo-CM', 'mk', 'mk-MK', 'ml', 'ml-IN', 'mn', 'mn-MN', 'mr', 'mr-IN', 'ms', 'ms-Arab', 'ms-Arab-BN', 'ms-Arab-MY', 'ms-BN', 'ms-MY', 'ms-SG', 'mt', 'mt-MT', 'mua', 'mua-CM', 'my', 'my-MM', 'mzn', 'mzn-IR', 'naq', 'naq-NA', 'nb', 'nb-NO', 'nb-SJ', 'nd', 'nd-ZW', 'ne', 'ne-IN', 'ne-NP', 'nl', 'nl-AW', 'nl-BE', 'nl-BQ', 'nl-CW', 'nl-NL', 'nl-SR', 'nl-SX', 'nmg', 'nmg-CM', 'nn', 'nn-NO', 'nnh', 'nnh-CM', 'nus', 'nus-SS', 'nyn', 'nyn-UG', 'om', 'om-ET', 'om-KE', 'or', 'or-IN', 'os', 'os-GE', 'os-RU', 'pa', 'pa-Arab', 'pa-Arab-PK', 'pa-IN', 'pl', 'pl-PL', 'ps', 'ps-AF', 'pt', 'pt-AO', 'pt-BR', 'pt-CV', 'pt-GW', 'pt-MO', 'pt-MZ', 'pt-PT', 'pt-ST', 'pt-TL', 'qu', 'qu-BO', 'qu-EC', 'qu-PE', 'rm', 'rm-CH', 'rn', 'rn-BI', 'ro', 'ro-MD', 'ro-RO', 'rof', 'rof-TZ', 'ru', 'ru-BY', 'ru-KG', 'ru-KZ', 'ru-MD', 'ru-RU', 'ru-UA', 'rw', 'rw-RW', 'rwk', 'rwk-TZ', 'sah', 'sah-RU', 'saq', 'saq-KE', 'sbp', 'sbp-TZ', 'se', 'se-FI', 'se-NO', 'se-SE', 'seh', 'seh-MZ', 'ses', 'ses-ML', 'sg', 'sg-CF', 'shi', 'shi-MA', 'shi-Tfng', 'shi-Tfng-MA', 'si', 'si-LK', 'sk', 'sk-SK', 'sl', 'sl-SI', 'smn', 'smn-FI', 'sn', 'sn-ZW', 'so', 'so-DJ', 'so-ET', 'so-KE', 'so-SO', 'sq', 'sq-AL', 'sq-MK', 'sq-XK', 'sr', 'sr-BA', 'sr-Latn', 'sr-Latn-BA', 'sr-Latn-ME', 'sr-Latn-RS', 'sr-Latn-XK', 'sr-ME', 'sr-RS', 'sr-XK', 'sv', 'sv-AX', 'sv-FI', 'sv-SE', 'sw', 'sw-CD', 'sw-KE', 'sw-TZ', 'sw-UG', 'ta', 'ta-IN', 'ta-LK', 'ta-MY', 'ta-SG', 'te', 'te-IN', 'teo', 'teo-KE', 'teo-UG', 'tg', 'tg-TJ', 'th', 'th-TH', 'ti', 'ti-ER', 'ti-ET', 'tk', 'tk-TM', 'to', 'to-TO', 'tr', 'tr-CY', 'tr-TR', 'twq', 'twq-NE', 'tzm', 'tzm-MA', 'ug', 'ug-CN', 'uk', 'uk-UA', 'ur', 'ur-IN', 'ur-PK', 'uz', 'uz-Arab', 'uz-Arab-AF', 'uz-Latn', 'uz-Latn-UZ', 'uz-UZ', 'vai', 'vai-LR', 'vai-Latn', 'vai-Latn-LR', 'vi', 'vi-VN', 'vun', 'vun-TZ', 'wae', 'wae-CH', 'xog', 'xog-UG', 'yav', 'yav-CM', 'yi', 'yi-001', 'yo', 'yo-BJ', 'yo-NG', 'yue', 'yue-HK', 'zgh', 'zgh-MA', 'zh', 'zh-Hans', 'zh-Hans-CN', 'zh-Hans-HK', 'zh-Hans-MO', 'zh-Hans-SG', 'zh-Hant', 'zh-Hant-HK', 'zh-Hant-MO', 'zh-Hant-TW', 'zu', 'zu-ZA']

    if len(sys.argv) > 2 and (sys.argv[2] == "--auto" or estimate == 0):
        print("auto")
        auto = True
        projectBase = None
        for root, subFolders, files in os.walk(path):
            if root.endswith('.xcodeproj') and os.path.islink(root) == False and "project.xcworkspace" in subFolders:
                # remember location of base
                projectBase = root
                print(root, subFolders)
                    
        try:
            assert(projectBase is not None)
        except:
            raise ValueError("Project File Not Found")

        # Get current project langs
        projLangs = []
        for lang in langs:
            #print("/".join(projectBase.split("/")[:-1])+"/"+projectBase.split("/")[:-1][-1]+"/"+lang+".lproj")
            if os.path.exists("/".join(projectBase.split("/")[:-1])+"/"+projectBase.split("/")[:-1][-1].replace("-", " ")+"/"+lang+".lproj"):
                projLangs.append(lang)
        langs = projLangs

        print("Found "+str(len(langs))+" Langs: ["+str(", ".join(langs))+"]")

        exports = " -exportLanguage ".join(langs)
        projectName = projectBase.split("/")[1].replace("-", "\ ")
        print(projectName)

        print("xcodebuild -exportLocalizations -localizationPath ./"+projectName+" -project "+str(projectBase).replace(" ", "\ ") + " -exportLanguage " + str(exports))
        os.system("xcodebuild -exportLocalizations -localizationPath ./"+projectName+" -project "+str(projectBase).replace(" ", "\ ") + " -exportLanguage " + str(exports))

        path = projectName+"/"

    for root, subFolders, files in os.walk(path):
        for file in files:
            if file.endswith('.xliff') and os.path.islink(os.path.join(root, file)) == False:
                #print(os.path.join(root, file))
                translateFile(file, root)
            elif (file.endswith('.ai') or file.endswith('.psd')) and os.path.islink(os.path.join(root, file)) == False:
                print(file)
                print("Found Image! Translating...")

    if auto and estimate is None:
        print("auto")
        
        exports = " -exportLanguage ".join(langs)
        projectName = projectBase.split("/")[1].replace("-", " ")
        projectName = projectName.replace(" ", "\ ")
        print(projectName)
        
        for lang in langs:
            # import one at a time
            print("xcodebuild -importLocalizations -localizationPath ./"+projectName +"/"+lang+".xliff -project "+str(projectBase).replace(" ", "\ "))
            os.system("xcodebuild -importLocalizations -localizationPath ./"+projectName +"/"+lang+".xliff -project "+str(projectBase).replace(" ", "\ "))
        
        path = projectName+"/"

    if estimate is not None:
        print("Estimate: $" + str(estimate) + " For " + str(count) + " characters in " + str(len(langs)) + " languages")

    print str(count)+" words"
