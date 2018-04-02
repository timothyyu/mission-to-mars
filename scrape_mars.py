#Scrape the NASA Mars News Site and collect the latest News Title and Paragragh Text
#Scrape featured image from JPL Featured Space Image
#Obtain Mars size vs. Earth diagram and alt/text caption
#Scrape Mars planet facts and information
#Obtain latest Mars weather information (@marswxreport, Twitter)
#Obtain full size image url links for all of Mars' Hemispheres

######

#Imports
from splinter import Browser #https://splinter.readthedocs.io/en/latest/
from bs4 import BeautifulSoup #https://www.crummy.com/software/BeautifulSoup/bs4/doc/
import pandas as pd
import time
import datetime
import requests
import json
import pymongo
#from selenium import webdriver

def init_browser():
    #Set path for splinter (chromedriver)
    executable_path = {'executable_path': 'chromedriver.exe'}
    #browser = Browser('chrome', **executable_path, headless=False)
    time.sleep(2)
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    #Declaration of dictionary to contain all scraped data (for function return)
    mars_news_scraped_dict = {}

    #Initalize browser and splinter/chromedriver
    browser = init_browser()
    time.sleep(2)
   
    #Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text
    #url to scrape
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    time.sleep(2.5)

    #set url in splinter/chromedriver
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    time.sleep(2)
    news_title = soup.find('div',class_='content_title') #.text     #get_text() will not work here
    news_title = news_title.text
    time.sleep(2.5)
    news_p = soup.find('div',class_='article_teaser_body') #.text
    news_p = news_p.text
    print(news_title)
    print(news_p)

    #Pass to dict
    mars_news_scraped_dict ["news_title"] = news_title
    mars_news_scraped_dict ["news_p_text"] = news_p    

    #Scrape featured image from JPL Featured Space Image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(2)
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(1.5)
    browser.click_link_by_partial_text('more info')

    #Pass html from splinter/chromedriver to be parsed by beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #Obtain relative image url from parsed html with beautiful soup
    img_url_part = soup.find('figure', class_='lede').find('img')['src']
    print("Relative url of image:")
    print(img_url_part)
    base_url =" https://www.jpl.nasa.gov"
    #Concatenate base_url and img_url_part
    print("Reconstructed full url of full size image:")
    print(base_url + img_url_part)

    #Pass to dict
    mars_news_scraped_dict["jpl_mars_image"] = base_url + img_url_part

    #Scrape Mars planet facts and information
    url = 'http://space-facts.com/mars/'
    browser.visit(url)
    time.sleep(3)

    #Pass html from splinter/chromedriver to be parsed by beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #Pass html from beautiful soup to the pd.read_html method:
    mars_facts_df = pd.read_html(html)[0]

    #https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_html.html
    mars_facts_df .columns=['description', 'value']
    mars_facts_df.set_index('description', inplace=True)

    #Mars size vs. Earth diagram scrape:
    diagram_text= soup.find('div',id="attachment_4837").find('img')['alt']
    diagram_url = soup.find('div',id="attachment_4837").find('img')['src']

    #Display output of table unformatted:
    mars_facts_df.to_html()

    #Url of Mars size vs. Earth diagram and alt text/caption:
    print(diagram_url)
    print(diagram_text)

    #Pass to dict
    mars_news_scraped_dict["diagram_img"]=diagram_url
    mars_news_scraped_dict["diagram_text"]=diagram_text

    #Examine dataframe conversion of table:
    print(mars_facts_df.head(15))

    #Latest mars weather information (@marswxreport, Twitter)
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(1.5)

    #Pass html from splinter/chromedriver to be parsed by beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    mars_weather_tweet_object = soup.find('div', attrs={"class": "tweet", "data-name": "Mars Weather"})
    mars_weather_tweet_enc_tags= mars_weather_tweet_object.find('p', 'tweet-text')
    current_mars_weather = mars_weather_tweet_enc_tags.get_text()
    print(current_mars_weather)
    
    #Pass to dict
    mars_news_scraped_dict["current_mars_weather"]=current_mars_weather

    #Mars Hemispheres title and image url
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    time.sleep(2)

    #Pass html from splinter/chromedriver to be parsed by beautiful soup
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #Base url for full image link reconstruction
    url_base = "https://astrogeology.usgs.gov"

    #List declaration
    hemisphere_url_images_complete = []
    url_list_incomplete = []

    #Find all div elements of the item class for url list construction
    result = soup.find_all('div', class_="item")

    #Incomplete url list construction (for hemisphere full size image links):
    for item in result:
        link = item.find('a')['href']
        print(item.find('a')['href'])
        url_list_incomplete.append(link)

    for incomplete_url in url_list_incomplete:
        #reconstruct complete url with url_base + incomplete_url
        url = url_base + incomplete_url

        #visit complete url with splinter/chromedriver   
        browser.visit(url)
        time.sleep(2)
        
        #Pass html from splinter/chromedriver to be parsed by beautiful soup
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        time.sleep(2)

        #Grab full image url and reconstruct with base url
        full_image_partial_url = soup.find('img', class_="wide-image")
        image = url_base + full_image_partial_url["src"]
        
        # Grab page title and remove "Enhanced" from string
        result2 = soup.find('h2', class_='title').text

        #title = result2.text
        title = result2.rsplit(' ', 1)[0]
        
        hemisphere_dict = {"Title": title, "Image URL": image}
        hemisphere_url_images_complete.append(hemisphere_dict)
        
      
        
    #print(hemisphere_url_images_complete)
    #print(json.dumps(hemisphere_url_images_complete,indent=1))
         #json.dumps not ideal for terminal output - dict object is not callable in this context
    print(hemisphere_url_images_complete)
    
    time.sleep(1.5)

    #Pass to dict
    mars_news_scraped_dict["hemisphere_images"] = hemisphere_url_images_complete

    time.sleep(0.5)
    
    #Close chrome window (splinter/chromedriver)
    browser.quit()

    #Return all scraped data as a dictionary
    return mars_news_scraped_dict
