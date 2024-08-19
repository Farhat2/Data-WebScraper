Task 1 : Web Scraping with Python

The goal of this task is to know more about web scraping using python , the web_scraper.py file contains a script that extract articles from Al Mayadeen website , gathers relevant metadata , and saves this information into Json files organized by month. 
The web scraper file includes classes, each class have methods responsible about something to do :
*Dataclass : used to store article metadata and content such as url,postid....
*SiteMapParser class : handle the parsing of the sitemap index and extraction of URL's, methods in it retrieve monthly sitemap URL's from the main one and extract article URL's from monthly sitemaps .
*ArticleScraper class : is responsible for scraping of individual articles .
*FileUtility class : handle saving extracted data to Json files , it convert data model instances to dictionaries and write them to a file .
*Main : Coordinate the overall process by integrating the sitemap parsing, article scraping, and file saving. Ensure the script processes all monthly sitemaps and organizes output by year and month. Implement error handling to manage network issues and unexpected data formats.

