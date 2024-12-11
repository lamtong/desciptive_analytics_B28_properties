# Python 3.12.4

# Package versions:
# - pandas 2.2.2
# - selenium 4.25.0

# This file contains the script that scrapes detailed features 
# of the sampled properties using their URLs, including:

# 1. Property Adress: Property Title in the webpage
# 2. Price (in £)
# 3. Type: Detached, Semi-Detached, Flat, Terraced, etc.
# 4. Number of Bedrooms
# 5. Number of Bathrooms
# 6. Real Estate Agent
# 7. URL: the URL of to the detailed webpage of each property

# And finally export all these scrapped data 
# to the scv file for later manipulation and analysis

# Import packages
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

# URLs of all properties in B28 + 0.5 miles radius, and URLs with filtered for Garden, Parking, and New Home
url_all = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E64&radius=1.0&sortType=6&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=&dontShow=retirement&furnishTypes=&keywords='
url_parking = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E64&radius=1.0&sortType=6&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=parking&dontShow=retirement&furnishTypes=&keywords='
url_garden = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E64&radius=1.0&sortType=6&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=garden&dontShow=retirement&furnishTypes=&keywords='
url_new = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E64&radius=1.0&sortType=6&propertyTypes=bungalow%2Cdetached%2Cflat%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=newHome&dontShow=retirement&furnishTypes=&keywords='

# Create Service Object
edgeService = Service(r"C:\\Users\blueb\\Downloads\\edgedriver_win64\\msedgedriver.exe")

# Create Webdriver Object
edgeDriver = webdriver.Edge(service = edgeService)

# Dictionary containing properties' attributes
properties_info = {'address': [],
                   'price': [],
                   'type': [],
                   'no_bed': [],
                   'no_bath': [],
                   'agent': [],
                   'url': []}


# Create Service Object
edgeService = Service(r"C:\\Users\blueb\\Downloads\\edgedriver_win64\\msedgedriver.exe")

# Create Webdriver Object
edgeDriver = webdriver.Edge(service = edgeService)

def scrappe():
    '''This function perform the web scrapping tasks:
    Args: None
    
    Returns: None
    '''
    # Find all div elements with the class 'property-information'
    house = edgeDriver.find_elements(By.CLASS_NAME, 'propertyCard-wrapper') # this class contains all info of a listed house

    for h in house:

        # Find URL
        id_tag = h.find_elements(By.TAG_NAME, 'a')
        id_attr = [t.get_attribute('href') for t in id_tag]
        properties_info['url'].append(id_attr[0]) # append found address into the dictionary
        
        # Find adress:
        add_class = h.find_elements(By.TAG_NAME, 'address')
        title_atr = [t.get_attribute('title') for t in add_class]
        properties_info['address'].append(title_atr[0]) # append found address into the dictionary

        # Find Price:
        price = h.find_elements(By.CLASS_NAME, 'propertyCard-priceValue')

        for pr in price:
            properties_info['price'].append(pr.text)

        # Find Types, Number of Bedrooms and Bathrooms
        infos = h.find_elements(By.CLASS_NAME, 'property-information')
        temp_info = []
        for x in infos:
            temp_info.append(x.text)
            temp_info = temp_info[0].split('\n')
            #print(temp_info)

        for i in range(len(temp_info)):

            if not temp_info[i].isdigit():
                properties_info['type'].append(temp_info[i])

                if (i+1) < len(temp_info) and temp_info[i+1].isdigit():
                    properties_info['no_bed'].append(temp_info[i+1])

                    if (i+2) < len(temp_info) and temp_info[i+2].isdigit():
                        properties_info['no_bath'].append(temp_info[i+2])

                    else: 
                        properties_info['no_bath'].append('not_specified')

                else:
                    properties_info['no_bed'].append('not_specified')
                    properties_info['no_bath'].append('not_specified')
        
        # Find Agent name:
        try:
            logo = h.find_element(By.CLASS_NAME, 'propertyCard-branchLogo')
            agent = logo.find_elements(By.TAG_NAME, 'a')
            alt_attributes = [img.get_attribute('title') for img in agent]
            properties_info['agent'].append(alt_attributes[0])
        except NoSuchElementException:
            properties_info['agent'].append('not_specified')
        
        
# Main code for looping through all web pages
try:
    edgeDriver.get(url_new)

    while True:
        print('Scrapping the current page...')
        scrappe() # scrappe the current page

        #Try finding the "Next" button
        try:
            next_button = WebDriverWait(edgeDriver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test='pagination-next']"))  # Adjust the locator as needed
            )
            next_button.click()  # Click the "Next" button
            print("Cliked Next")
            time.sleep(2)  # Pause to allow the page to load
        except (NoSuchElementException, TimeoutException):
            print("No more pages to scrape.")
            break  # Break the loop if there are no more pages

finally:
    # Clean up and close the driver
    edgeDriver.quit()   

# parsing to the dataframe
df = pd.DataFrame(properties_info)

# export to csv
df.to_csv('[new]B28_plus_1mile_rightmove_4_Nov.csv', index = False)