import requests
import re
import numpy as np
import os
import sys

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
}


def GetUrlsForPages(nameForPerson):
    Str = "https://www.yeitu.com/tag/" + nameForPerson + "/.page=+[0-9]*"
    urlForPerson = "https://www.yeitu.com/tag/" + nameForPerson + "/"
    response = requests.get(url=urlForPerson, headers=headers)
    contents = response.text
    pages = re.findall(Str, contents)
    pages = np.unique(pages)
    urlForPerson = [urlForPerson]
    if len(pages) == 0:
        return urlForPerson
    else:
        return pages


def GetUrlsForEachSet(urlForPerson):
    response = requests.get(url=urlForPerson, headers=headers)
    # print(response.request.headers)
    # print(response.text)
    contents = response.text
    # print(contents)
    urls = re.findall(
        'https://www.yeitu.com/.*?/.*?/+[_0123456789]*.html', contents)
    urls = np.unique(urls)
    return (urls)


def GetSumForEachSet(urlForSet):
    response = requests.get(url=urlForSet, headers=headers)
    # print(response.request.headers)
    # print(response.text)
    contents = response.text
    # print(contents)
    number = re.findall(
        '<span class="imageset-sum">/ +[0-9]*', contents)
    number = re.findall('[0-9]+\d|[0-9]', number[0])
    if len(number) >= 1:
        number = int(number[0])
    else:
        number = 2
    return number


def GetDateForEachSet(urlForSet):
    numbers = re.findall("[0-9]+\d", urlForSet)
    Date = numbers[0]
    return Date


def GenerateUrlsForEachPicture(urlForSet, number):
    urlsForPictures = []
    urlForSet = urlForSet[0:-5]
    for i in range(2, number):
        urlsForPictures.append(urlForSet + '_' + str(i) + '.html')
    return urlsForPictures


def GetUrlsForPictures(urlsForPictures, Date):
    urlsOfpictures = []
    for i in range(len(urlsForPictures)):
        response = requests.get(url=urlsForPictures[i], headers=headers)
        contents = response.text
        # StrForSearchPictures = 'src="https://file.jiutuvip.com/' + Date[0:4] + '/' + Date[
        #                                                                              4:8] + '/' + Date + '+[0-9]*.jpg'
        # A new way to get urlsOfpictures
        StrForSearchPictures = '<a href=".*?"><img alt=".*?" src="(.*?)"'
        url = re.findall(StrForSearchPictures, contents)
        for item in url:
            urlsOfpictures.append(item)
    urlsOfpictures = np.unique(urlsOfpictures)
    return urlsOfpictures


def DownloadPictures(urlsOfpictures, m, n, name):
    os.mkdir(name + "_page" + str(m) + "_" + str(n))
    for i in range(len(urlsOfpictures)):
        # url = urlsOfpictures[i][5:]
        # A new way to get urlsOfpictures
        url = urlsOfpictures[i]
        # print(url)
        res = requests.get(url=url, headers=headers)
        with open(name + "_page" + str(m) + "_" + str(n) + "/" + str(i) + '.jpg', 'wb') as f:
            # print(i)
            f.write(res.content)


global emptyUrls
global emptyFiles
emptyUrls = []
emptyFiles = []


def Process(name):
    urlForPages = GetUrlsForPages(name)  # Get urls of all pages
    print(urlForPages)
    for j in range(len(urlForPages)):
        print(name, "page", j)
        url = urlForPages[j]
        urlsForsets = GetUrlsForEachSet(url)  # Get urls of each set
        if len(urlsForsets) == 0:
            print(name + " <- No such name or classification")
            continue
        print(urlsForsets)
        print(len(urlsForsets))
        for i in range(len(urlsForsets)):
            Date = GetDateForEachSet(urlsForsets[i])  # Get date of each set (useless)
            print(name, "page: ", j, "set: ", i, ": done Date")
            # print(Date)
            Sum = GetSumForEachSet(urlsForsets[i])  # Get the number of pictures a set contains
            print(name, "page: ", j, "set: ", i, ": done Sum")
            print(Sum)
            urlsForPictures = GenerateUrlsForEachPicture(urlsForsets[i], Sum)  # Get urls of each picture
            print(name, "page: ", j, "set: ", i, ": done urlsForPictures")
            # print(urlsForPictures)
            urlsOfPictures = GetUrlsForPictures(urlsForPictures, Date)  # Get downloading urls of each picture
            print(name, "page: ", j, "set: ", i, ": done urlsOfPictures")
            # Check out whether "urlsOfPictures" is empty
            if len(urlsOfPictures) == 0:
                print(name, "Empty URL: ", "page: ", j, "set: ", i)
                print(name, "The empty url: ", urlsForsets[i])
                strUrls = name + "The empty url: " + urlsForsets[i]
                emptyUrls.append(strUrls)
                strFiles = name + "page: " + str(j) + "set: " + str(i)
                emptyFiles.append(strFiles)
            # print(urlsOfPictures)
            DownloadPictures(urlsOfPictures, j, i, name)  # Finish downloading
            print(name, "page: ", j, "set: ", i, ": done Download")


if __name__ == '__main__':
    print("Explanation:\n"
          'The function of this code is to crawl the pictures on "yeitu.com"\n'
          'If you want to crawl the pictures of a specific person or classification, \n'
          'you can just input the tag of the person or classification.\n'
          'Certainly, the tag should exist. You must check it by yourself.\n'
          'Though a wrong tag will not cause the code to report error, you can not get what you want.\n'
          'For example: you can try this tag -- "mumuxiMmx".\n'
          'Then, the pictures will be downloaded automatically to the directory where the code is located\n'
          'The process of downloading will take a while, and some process prompts will be given.')
    print("-----------------------------------------------------------------------------------------------------------")
    flag = True
    names = []
    while flag == True:
        name = input("Please input the name or classification: ")
        names.append(name)
        FlagStr = input(" Do you want to input another name or classification ? (y/n): ")
        while FlagStr != 'y' and FlagStr != 'n':
            FlagStr = input('Please input again (y/n): ')
        if FlagStr == 'y':
            flag = True
        elif FlagStr == 'n':
            flag = False

    for name in names:
        Process(name)
    print(emptyUrls)
    print(emptyFiles)
