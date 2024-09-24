# Data-WebScraper Project

### Task 1 : Web Scraping with Python

Overview
This project is a Python-based web scraper that extracts articles from the Al Mayadeen website by utilizing its sitemap. The scraper collects relevant metadata (e.g., title, author, keywords) and full article content. The extracted data is stored in JSON files, organized by year and month.
The goal of this task is to know more about web scraping using python , the web_scraper.py file contains a script that extract articles from Al Mayadeen website , gathers relevant metadata , and saves this information into Json files organized by month. 
The web scraper file includes classes, each class have methods responsible about something to do :

*Dataclass : used to store article metadata and content such as url,postid....

*SiteMapParser class : handle the parsing of the sitemap index and extraction of URL's, methods in it retrieve monthly sitemap URL's from the main one and extract article URL's from monthly sitemaps .

*ArticleScraper class : is responsible for scraping of individual articles .

*FileUtility class : handle saving extracted data to Json files , it convert data model instances to dictionaries and write them to a file .

*Main : Coordinate the overall process by integrating the sitemap parsing, article scraping, and file saving. Ensure the script processes all monthly sitemaps and organizes output by year and month. Implement error handling to manage network issues and unexpected data formats.

when it finishes running , the json files are saved by month in a directory ("output") 
use this link to know more : https://youtu.be/1PIMCbVE6J0
 

![](C:\Users\HP\Desktop\output.png)




### Task 2 : Data Storage in MongoDB and Flask API Development

in this task we will ad 2 python files to our project , one for data storage , and the another one is for the Flask API .

- Data_storage.py file : in this file we will extend our work from task 1 by focusing on storing collected data into a mongodb database ( NoSQL database) . This code(code in data_storage.py) connects to a MongoDB instance, loads the JSON data, and inserts it into a collection named articles within the almayadeen database.

![](C:\Users\HP\Desktop\databaseshowing.png)
![](C:\Users\HP\Desktop\databaseshowing2.png)
- app.py file : this file we Build a Flask API that exposes endpoints for querying and aggregating the data, and Implement various aggregation endpoints, such as top keywords, top authors, articles by publication date, and articles by word count. Each end point returns what we want , and the way of testing is by  running the app.py script The Flask server should start, and you can access the API endpoints by navigating to http://127.0.0.1:5000/ followed by the endpoint path in your web browser or using a tool like Postman , in the video you will see many endpoints how it runs .
example : 
![](C:\Users\HP\Desktop\app.py.png)
![](C:\Users\HP\Desktop\top_key.png)

use this link to know more : https://youtu.be/yCqUdKKO9kQ
                             https://youtu.be/062G_6WtpQo



### Task 3 : Data Visualization using amCharts

in this task we should show each endpoint in a nice and simple way , we use charts each endpoint have its own chart , and each kind of data should use for it a chart , 
Amchart is a good resource for using many kinds of charts , it provides the js code of it . 