# App-Translator--iOS
Automatically takes exported strings from Xcode and translates them to any language.

By [Matthew Paletta](http://techguyification.com).

Translating iOS Apps has never been easier (or cheaper)

**App Translator** takes your localization workflow already in Xcode, and automates it. The basic goal of **App Translator** is to let computers translate themselves, so you don't have to (or hire someone to do so).

## Installation

Open ![Google Cloud Console](https://console.cloud.google.com), and create a new API key for Google Cloud Translation API.  You will also need to setup billing for your account.

Copy your API key from Google Cloud Console into translate.py

## USAGE

**Simple Form** was designed to be customized as you need to. Basically it's a stack of components that
are invoked to create a complete html input for you, which by default contains label, hints, errors
and the input itself. It does not aim to create a lot of different logic from the default Rails
form helpers, as they do a great job by themselves. Instead, **Simple Form** acts as a DSL and just
maps your input type (retrieved from the column definition in the database) to a specific helper method.

To start using **Simple Form** you just have to use the helper it provides:

Add any localizations you want to use in the "Localizations" section of the project manager.
- Make sure to check off "Use Base Internalization"

Export localizations from Xcode through the menu bar.

![Export Localization](https://raw.github.com/mattpaletta/App-Translator-iOS/master/export_localization.png)

Run App-Translator
```console
python localizeFile.py {FOLDER NAME}
```

Back in Xcode, import the same localization files through the menu bar.  App-Translator will save the translated files back into the original files.

![Import Localization](https://raw.github.com/mattpaletta/App-Translator-iOS/master/import_localization.png)


#Tested Languages

Source Language         | 
------------------------|
English               |

Translated Language     | 
------------------------|
Chinese (Traditional)   |
Chinese (Simplified)    |
English                 |
French                  |
German                  |
Italian                 |
Japanese                |
Korean                  |
Portugese (Brazil)      |
Portugese (Portugal)    |
Russian                 |
Spanish                 |


## Information

### Questions, Comments, Concerns, Queries, Qwibbles?

If you have any questions, comments, or concerns please leave them in the GitHub
Issues tracker:

https://github.com/mattpaletta/App-Translator-iOS/issues

### Bug reports

If you discover any bugs, feel free to create an issue on GitHub. Please add as much information as
possible to help us fixing the possible bug. We also encourage you to help even more by forking and
sending us a pull request.

https://github.com/mattpaletta/App-Translator-iOS/issues

## Maintainers

* Matthew Paletta (https://github.com/mattpaletta)

## License

GPL-3.0 License. Copyright 2017 Matthew Paletta. http://techguyification.com
