from lxml import html
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Scraper goes to starting URL, gathers all of the URLs for the different years IM results.
# Then, iterates through the pagination per race, and stores in a CSV / Pandas DF.

# Get starting URL in place.
url = 'http://www.ironman.com/triathlon/events/americas/ironman/world-championship/results.aspx?rd=20161008#axzz4rGjY7ruv'
response = requests.get(url)
html = response.content

# Translate to BeautifulSoup object
soup = BeautifulSoup(html, 'lxml')

# Get all race links.
raceLinks = []
for ul in soup.find_all('ul', {'id': 'raceResults'}):
    for link in ul.find_all('a', href=True):
        raceLinks.append(link['href'])

# get rid of blank links
raceLinks = [x for x in raceLinks if x]
# get rid of 2002 link, as results in bad format and break code.
raceLinksFin = raceLinks[0:-1]


#Set a header
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

# Loop through races to gather data
mDF = pd.DataFrame()
for race in raceLinksFin:

    # get part of URL that corresponds to date to identify which year results belong to
    date = race[92:]

    # Get number of pages
    response = requests.get(race)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    numberOfPages = []
    for div in soup.find_all('div', {'class': 'pagination'}):
        for span in div.find_all('span'):
            numberOfPages.append(span.get_text())

    # clean non-numerics from list of gathered data
    cleaned = [x for x in numberOfPages if x.isdigit()]
    # convert to int
    ints = [int(x) for x in cleaned]
    # get max page numbers
    maxPages = max(ints)

    # Starting URL, as route is different for page 1
    for div in soup.find_all('div', {'class': 'pagination'}):
        for link in div.find_all('a', href=True):
            firstLink = link['href']

            # build link route to loop through paginated pages
            part1 = firstLink[0:91]
            part2 = firstLink[93:]

    # Get data from page 1
    df = pd.DataFrame()

    #read the file as a browser
    r = requests.get(race, headers=header)
    #read the text
    df_intial = pd.read_html(r.text, attrs={'id': 'eventResults'})

    # append data to dataframe, adding date to identify race year
    df = df.append(df_intial)
    df['Date'] = date
    mDF = mDF.append(df)

    # Loop through remaining pages
    df_2 = pd.DataFrame()
    i = 2
    while i < maxPages:  # 116
        securl = part1 + str("=") + str(i) + part2
        print(securl)
        r2 = requests.get(securl, headers=header)
        df_temp = pd.read_html(r2.text, attrs={'id': 'eventResults'})
        #print(df_temp)
        df_2 = df_2.append(df_temp)
        # print(df)
        i = i + 1
    df_2['Date'] = date
    mDF = mDF.append(df_2)

# write to a csv, or output to
mDF.to_csv('results.csv')