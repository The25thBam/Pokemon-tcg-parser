#/usr/bin/python3
from platform import system as OSdetect
from os import getcwd, chdir, rename
from os import makedirs as mkdir
from requests import Session
from wget import download
from bs4 import BeautifulSoup as bsp

# Prepares the HTML to be parsed
def prepareToParse(link):
    req = Session()
    html = req.get(link, cookies={"display":"images"})
    soup = bsp(html.text, "html5lib")
    return soup

# Some names had the "amp;" string after the "&" symbol.
# This function removes it
def removeAmpText(text):
    if "amp;" in text:
        text = text.replace("amp;", "")
        return text
    return text

# Gets the expansion title from
def getExpansionTitle(to_parse):
    for h1 in to_parse.find_all("h1"):
        e_title = str(h1)
        e_title = e_title[27::]
        e_title = e_title[0:-15]
        e_title = removeAmpText(e_title)
        return e_title

# Detects the shell script language your pc uses by default
def shellScriptDetect():
    if OSdetect() == "Windows":
        return "Batch"
    else:
        return "Bash"

# Fixes path routes if in Windows
def fixPath(path):
    if shellScriptDetect() == "Batch":
        path = path.replace("/", "\\")
    return path

# Gets all card names from the current expansion
def getCardNames(to_parse):
    names = []
    for img in to_parse.find_all("img"):
        name = str(img["alt"])
        name = name.split()
        number = name[-1].split("/")[0].zfill(3)
        name = " ".join(name).split("(")[0][:-1]
        name = f"{number} {name}"
        names.append(name)
    return names

# Gets all URLs of the cards in the current expansion
def getCardURLs(to_parse):
    card_URLs = []
    for img in to_parse.find_all("img"):
        card_URL = img["src"]
        card_URLs.append(card_URL)
    return card_URLs

# Gets the card names assigned in the website for the current expansion
def getOldNames(links):
    old_names = []
    for link in links:
        name = link.split("/")[-1]
        old_names.append(name)
    return old_names

# Self explainatory
def changeDirectory(path):
    path = fixPath(f"{getcwd()}/{path}")
    chdir(path)

# Downloads the cards from the current expansion
def downloadCards(card_URLs, cards, expansion_set):
    for URL in card_URLs:
        if "no-image" not in URL:
            download(URL)

# Fixes names into Windows format
def namesFix(names):
    for i in range(len(names)):
        if "?" in names[i]:
            names[i] = names[i].replace("?", "¿")
        if ":" in names[i]:
            names[i] = names[i].replace(":", ";")

# Renames the cards from the names in the website to their actual names
# (leaves a log if errors are presented)
def renameCards(old_names, new_names, expansion):
    logname = fixPath("../../error.log")
    count = -1
    with open(logname, "a+") as error:
        for name in old_names:
            count += 1
            try:
                if ".jpg" in name:
                    rename(name, f"{new_names[old_names.index(name)]}.jpg")
                elif ".png" in name:
                    rename(name, f"{new_names[old_names.index(name)]}.png")
                else:
                    print(f"unknown file format: {name} in {getcwd()}")
            except FileNotFoundError:
                error.write(f"Card not found in website. Could not download {new_names[count]} from {getExpansionTitle(expansion)}\n")

# Some fixes in file naming
def additionalNameFixes(names):
    for i in range(len(names)):
        if "SWSH" in names[i]:
            names[i] = names[i].replace("SWSH", "")
        if ")" in names[i] and "(" not in names[i]:
            names[i] = names[i].replace(")", "")

if __name__ == "__main__":
    expansions = []
    # Reads which expansions are intended to be downloaded from the "expansions" file
    with open("expansions", "rt") as expansions_file:
        for line in expansions_file:
            if line[0] != "#":
                expansion_ID = int(line.split("-")[0])
                expansions.append(expansion_ID)
    # Cards parsing and downloading
    for expansion in expansions:
        url = f"https://www.tcgcollector.com/cards?expansion-{expansion}=on"
        website = prepareToParse(url)
        expansion_title = getExpansionTitle(website)
        if expansion_title == "":
            expansion_title = "empty"
        folder_path = (f"Pokemon/{str(expansion).zfill(3)} {expansion_title}")
        folder_path = fixPath(folder_path)
        mkdir(folder_path, exist_ok=True)
        changeDirectory(folder_path)
        card_urls = getCardURLs(website)
        old_card_names = getOldNames(card_urls)
        new_card_names = getCardNames(website)
        if shellScriptDetect() == "Batch":
            namesFix(new_card_names)
        additionalNameFixes(new_card_names)
        downloadCards(card_urls, new_card_names, expansion_title)
        renameCards(old_card_names, new_card_names, website)
        changeDirectory(fixPath("../.."))
    # Sets up the end of the execution in the log
    with open("error.log", "a+") as error:
        error.write("---------------------------------------------------------------------------------\n")
        error.seek(0)
        line = str(error.readline())
        if line[0] == "-":
            error.truncate(0)
