from splinter import Browser 
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pymongo
from pymongo import MongoClient
from flask import Flask, render_template

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

def scrape():
    
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    #All NASA information
    Mars_nasa_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(Mars_nasa_url)

    #create HTML object
    html = browser.html
    #parse HTML with BEAUTIFULSOUP
    soup = BeautifulSoup(html, 'html.parser')

###########################################################
    #visit and pull data from website NASA url
############################################################

    first_item = soup.find('li', class_='slide')


    title = first_item.find('div', class_='content_title').text

    news_p = first_item.find('div', class_='article_teaser_body').text


#################################################
# Mars Images & URL
#################################################
    
    images_url = 'https://www.jpl.nasa.gov/images?search=&category=Mars'
    browser.visit(images_url)

    html2 = browser.html
    soup2 = BeautifulSoup(html2, 'html.parser')
    featured_image_url = soup2.find('img', class_= 'BaseImage')['src']
    

###############################################
#Mars Table Description & Numbers
###############################################

    mars_facts_url = 'https://space-facts.com/mars/'
    mars_facts_html = pd.read_html(mars_facts_url)
    
    #html format data 1st index compares Mars to Earth
    mars_earth_df = mars_facts_html[1]
   
    #Pulling a datframe and dropping column and setting index to Description
    mars_df = mars_earth_df.drop(columns=['Earth']).rename(columns={'Mars - Earth Comparison': 'Description'})
    mars_df = mars_df.set_index('Description')
    mars_df.to_html('mars_facts.html')
    
    #convert mars dataframe to html string
    mars_facts_string = mars_df.to_html (header=True, index=True)


    #Mars Hemispheres
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    html4 = browser.html
    soup4 = BeautifulSoup(html4, 'html.parser')
    hemosphere_urls = soup4.find_all('div', class_='description')

    main_url = 'https://astrogeology.usgs.gov'
    hemisphere_image_urls = []
    for item in hemosphere_urls:
        each_url = item.find('a')['href']
        full_url = main_url + each_url
        title = item.find('h3').text
    
        hemisphere_image_urls.append({'Title': title, 'Hemisphere Url':full_url})


    #close browser
    browser.quit()

    #Put all data in a dict and push to the MongoDB
    all_data_mars = {
    'Title' : title,
    'Mars_Paragraph': news_p,
    'Featured_image': featured_image_url,
    'Mars_Facts_Table': mars_facts_string,
    'Hemisphere_image_urls': hemisphere_image_urls,
    }
            
    collection.insert(all_data_mars)
    
    return all_data_mars