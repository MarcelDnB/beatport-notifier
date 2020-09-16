import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import re
import time

""" CONFIG -- VARIABLES """
configDict = dict()
userAgent = str()
URLs = str()
fromDate = str()
headers = str()
todayDate = str()
yourEmail = str()
toEmail = str()
smtpGooglePass = str()
date = str()


def importConfig():
    global configDict
    global userAgent
    global URLs
    global fromDate
    global headers
    global todayDate
    global yourEmail
    global toEmail
    global smtpGooglePass
    with open("config.config", "r") as config:
        for line in config:
            match = re.search(r"(^[\w]*):[\[]?([\w\d:/.*\",(;\)-?\\@]*)", line)
            configDict[match[1]] = match[2]

    userAgent = configDict['userAgent']
    URLs = configDict['URLS'].split(",")
    fromDate = configDict['fromDate']
    headers = {
        "User-Agent": userAgent
    }
    todayDate = datetime.today().strftime(r'%Y-%m-%d')
    yourEmail = configDict['yourEmail']
    toEmail = configDict['toEmail']
    smtpGooglePass = configDict['smtpGooglePass']


def sendEmail(bodyMsg):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(yourEmail, smtpGooglePass)

    subject = "New Albums Found On Beatport!"
    body = bodyMsg

    msg = f"Subject: {subject}\n\n{body}".encode('utf-8')
    server.sendmail("BeatportTracking@gigi.com", toEmail, msg)
    server.quit()


def description(soup):
    desc = soup.find(
        "div", {"class": "interior-expandable"})
    if "<br/>" in str(desc):
        descBr = str(desc).replace("<br/>", "")
        newSoap = BeautifulSoup(str(descBr), "html.parser")
        desc = newSoap.string
        desc = desc.strip()
    else:
        desc = desc.string
        desc = desc.strip()
    return desc


def tagGet(newSoup):
    """ HYPE? EXCLUSIVE? """
    hype = newSoup.body.find_all(
        "span", {"class": "hype-marker"})
    exclusive = newSoup.body.find_all(
        "span", {"class": "exclusive-marker"})
    preOrder = newSoup.body.find_all(
        "span", {"class": "preorder-marker"})
    tagList = list()

    if not hype:
        hype = ""
    else:
        tagList.append("HYPE!")

    if not exclusive:
        exclusive = ""
    else:
        tagList.append("EXCLUSIVE!")

    if not preOrder:
        preOrder = ""
    else:
        tagList.append("Pre-Order")

    if not tagList:
        tagList.append("No tags")
    return tagList


def getArtist(newSoup):
    artist = list()
    Artist = newSoup.find_all(
        "span", {"class": "value"})
    if "data-artist" in str(Artist[3]):
        artistSoup = BeautifulSoup(str(Artist[3]), features="lxml")
        artist = artistSoup.find_all("a")
        artist = [i.string for i in artist]
    else:
        artist.append(Artist[3].string)
    return artist


def getCatalogId(newSoup):
    Catalog = newSoup.find_all(
        "span", {"class": "value"})
    catalog = str()
    try:
        catalog = Catalog[2].string
    except:
        catalog = "Unable to get catalog id."
    return catalog


def albumLinkAndImage(soup2):
    AlbumLink = soup2.find_all(
        "a", href=True)
    AlbumImage = soup2.find_all(
        "img")
    magicList = list()
    imgList = list()
    for a in AlbumLink:
        magicList.append(a["href"])
    for b in AlbumImage:
        imgList.append((b["data-src"]))
    albumLink = "https://www.beatport.com" + magicList[0]
    try:
        albumImage = imgList[0]
    except:
        albumImage = "Unable to get album art."
    return albumLink, albumImage


def formatter(labelName, artist, tagList, catalog, albumName, descr, date):
    bodyArgs = str()
    bodyArgs = bodyArgs + labelName + ":\n    " + "Artist/s: " + ', '.join(artist) + "\n    " +  \
        "Album Name: " + albumName + "\n    " + "Release Date: " + date + "\n    " + "Catalog: " + catalog + \
        "\n    " + "BeatportTag/s: " + \
        ', '.join(tagList) + "\n    " + \
        "Description: \n" + descr + "\n\n\n\n"
    return bodyArgs


def shouldSend(bodyArg):
    if bodyArg != "" and bodyArg != None and bodyArg != "None":
        sendEmail(bodyArg)


def getAlbumName(soup2):
    AlbumName = soup2.find(
        "p", {"class": "buk-horz-release-title"})
    return AlbumName.string


def getDate(soup2):
    dateWithTag = soup2.find("p", {"class": "buk-horz-release-released"})
    date = dateWithTag.string
    return date


def getAlbumEntry(URL):
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return page, soup


def processAlbumEntry(URL):
    global todayDate
    global date
    bodyArg = str()
    page, soup = getAlbumEntry(URL)
    for i in range(1, 26):
        entry = soup.findAll("li", {"data-ec-position": str(i)})
        soup2 = BeautifulSoup(str(entry[0]), "html.parser")
        date = getDate(soup2)
        if fromDate != "":
            todayDate = fromDate
        if(date == todayDate):
            albumName = getAlbumName(soup2)
            labelName = soup.h1.string
            """ ALBUM LINK AND COVER """
            albumLink, albumImage = albumLinkAndImage(soup2)
            NEWURL = albumLink
            newPage = requests.get(NEWURL, headers=headers)
            newSoup = BeautifulSoup(newPage.content, "html.parser")
            """ CATALOG ID """
            catalog = getCatalogId(newSoup)
            """ ARTIST NAME """
            artist = getArtist(newSoup)
            """ TAG LIST """
            tagList = tagGet(newSoup)
            """ DESCRIPTION """
            descr = description(newSoup)
            bodyArg = formatter(labelName, artist, tagList,
                                catalog, albumName, descr, date)

    return bodyArg


def processURL():
    bodyArg = str()
    for URL in URLs:
        bodyArg = bodyArg + processAlbumEntry(URL)
    return bodyArg


def run():
    importConfig()
    bodyArg = processURL()
    shouldSend(bodyArg)


run()
