import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import re
import time

configDict = dict()
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
bodyArg = str()


def sendEmail(bodyMsg):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(yourEmail, smtpGooglePass)

    subject = "New Albums Found On Beatport!"
    body = bodyMsg

    msg = f"Subject: {subject}\n\n{body}"
    server.sendmail("BeatportTracking@gigi.com", toEmail, msg)
    server.quit()


if fromDate != "":
    date = fromDate


def run():
    global todayDate
    global bodyArg
    for URL in URLs:
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        for i in range(1, 26):
            entry = soup.findAll("li", {"data-ec-position": str(i)})
            soup2 = BeautifulSoup(str(entry[0]), "html.parser")
            AlbumName = soup2.find(
                "p", {"class": "buk-horz-release-title"})
            dateWithTag = soup2.find(
                "p", {"class": "buk-horz-release-released"})
            date = dateWithTag.string
            albumName = AlbumName.string
            labelName = soup.h1.string

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
            NEWURL = albumLink
            newPage = requests.get(NEWURL, headers=headers)
            newSoup = BeautifulSoup(newPage.content, "html.parser")
            Catalog = newSoup.find_all(
                "span", {"class": "value"})
            catalog = str()
            try:
                catalog = Catalog[2].string
            except:
                catalog = "Unable to get catalog id."
            if fromDate != "":
                todayDate = fromDate
            if(date == todayDate):
                bodyArg = bodyArg + "\n\n" + labelName + ":\n    " + \
                    albumName + ": " + date + "\n    " + "Catalog: " + catalog
    if bodyArg != "":
        sendEmail(bodyArg)


run()
