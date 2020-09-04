import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import re

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
    while(1):
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
                if fromDate != "":
                    todayDate = fromDate
                if(date == todayDate):
                    bodyArg = bodyArg + "\n\n" + labelName + ":\n    " + albumName + ": " + date

        if bodyArg != "":
            sendEmail(bodyArg)
            return


run()
