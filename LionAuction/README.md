# LionAuction Project
***
This project was done individually by Tejas Chadha Marimuthu for CMPSC 431W.

## Table of Contents
1. [General Info](#general-info)
2. [Organization of Code](#organization-of-code)
3. [Features](#features)
4. [Instructions](#instructions)

## General Info
***
This is LionAuction Checkpoint, which allows users to log into homepage of site. This project utilizes HTML, FLASK, and Python for the webpages functionality. SQLite is used as the query language to manage the database.

## Organization of Code
***
Starting from the top of the files, dataset folder contains the csv files with the provided data needed for the database. Static contains files that do not change during the running of the code, such as images, javascript files, and CSS file. Template folder holds all the html pages that are loaded when the program are run. There is a base template here that utilizes jinja for template inheritance.
### app.py
***
A Python file that is used to run a development server which connects our front-end to the back-end. It holds the necessary functionality to interact/manage the lionauction database. This file also holds the routing functions so that user can navigate efficiently between webpages. 

The function index() routes user to home page (home.html) on GET request. If a post request is received on login page, then user is navigated to either login page (upon failure) or home page (home.html). valid_user() verifies user credentials that were entered on login page.
#### Routing Functions
```
def index();
def login();
def categories():
def local_vendors():
def home():
def listings():
def account_info():
def update_account_info(): 
def update_item_info():
def add_listing():
def delete_listing_table():
def delete_listing(data):
def item(data):
```

### data.py
***
Python file that recreates the database if it does not exist.

## Instructions
***
During the implementation of this project, I used Visual Studio Code in MacOS environment to work on this assignment. To run the code, simply open the terminal, navigate (cd) into the directory where the project is stored. Then type "python3 app.py" if on mac. This should boot up the server and prompt you in the terminal the location of the website. Open that link in a web browser such as Safari to view the website and interact with it. The database will be automatically created when running the program.

### Possible Issue:
***
Bidding is not complete yet along with notifications.