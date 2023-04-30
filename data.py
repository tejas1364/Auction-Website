import sqlite3 as sql
import pandas as pd
import hashlib


'''
Function Name: importUserData()
Parameters: None
Purpose: Create Users table and import Users data into database.
'''
def importUsersData():
    connection = sql.connect('database.db')
    connection.execute("PRAGMA foreign_keys = 1")
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Users(email TEXT PRIMARY KEY, password TEXT);') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Users LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        users = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Users.csv')
        for p in users["password"]:
            p2 = hashlib.sha256(p.encode())
            p2 = p2.hexdigest()
            users['password'] = users['password'].str.replace(p, p2)
        users.to_sql('Users', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importSellerData()
Parameters: None
Purpose: Create Seller table and import seller data into database.
'''
def importSellerData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Sellers(email TEXT PRIMARY KEY, bank_routing_number TEXT, bank_account_number INT, balance REAL, FOREIGN KEY (email) REFERENCES Users (email));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Sellers LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Sellers.csv')
        data.to_sql('Sellers', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importVendorData()
Parameters: None
Purpose: Create Local Vendor table and import Vendor data into database.
'''
def importVendorData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Local_Vendors(email TEXT PRIMARY KEY, business_name TEXT, business_address_id TEXT, customer_service_phone_number TEXT, FOREIGN KEY (email) REFERENCES Sellers (email), FOREIGN KEY (business_address_id) REFERENCES Address (address_id));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Local_Vendors LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Local_Vendors.csv')
        data.to_sql('Local_Vendors', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importBiddersData()
Parameters: None
Purpose: Create Bidders table and import Bidders data into database.
'''
def importBiddersData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Bidders(email TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, gender TEXT, age INT, home_address_id TEXT, major TEXT, FOREIGN KEY (email) REFERENCES Users (email), FOREIGN KEY (home_address_id) REFERENCES Address (address_id));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Bidders LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Bidders.csv')
        data.to_sql('Bidders', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importHelpDeskData()
Parameters: None
Purpose: Create HelpDesk table and import HelpDesk data into database.
'''
def importHelpDeskData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS HelpDesk(email TEXT PRIMARY KEY, position TEXT, FOREIGN KEY (email) REFERENCES Users (email));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM HelpDesk LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Helpdesk.csv')
        data.to_sql('HelpDesk', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importRequestsData()
Parameters: None
Purpose: Create Requests table and import Requests data into database.
'''
def importRequestsData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Requests(request_id INT PRIMARY KEY, sender_email TEXT, helpdesk_staff_email TEXT, request_type TEXT, request_desc TEXT, request_status INT, FOREIGN KEY (helpdesk_staff_email) REFERENCES HelpDesk (email), FOREIGN KEY (sender_email) REFERENCES Users (email));') #Create table if it doesn't exist *Might have to make a join between Bidders and Sellers
    cursor.execute('SELECT * FROM Requests LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Requests.csv')
        data.to_sql('Requests', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importAuctionListingsData()
Parameters: None
Purpose: Create Local Vendor table and import Vendor data into database.
'''
def importAuctionListingsData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Auction_Listings(seller_email TEXT, listing_id INT, category TEXT, auction_title TEXT, product_name TEXT, product_description TEXT, quantity INT, reserve_price REAL, max_bids INT, status INT, PRIMARY KEY(seller_email, listing_id), FOREIGN KEY (seller_email) REFERENCES Sellers (email), FOREIGN KEY (category) REFERENCES Categories (category_name));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Auction_Listings LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Auction_Listings.csv')
        data.to_sql('Auction_Listings', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importBidsData()
Parameters: None
Purpose: Create Bids table and import bids data into database.
'''
def importBidsData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Bids(bid_id INT PRIMARY KEY, seller_email TEXT, listing_id INT, bidder_email TEXT, bid_price REAL, FOREIGN KEY (seller_email) REFERENCES Auction_Listings (seller_email), FOREIGN KEY (bidder_email) REFERENCES Bidders (email), FOREIGN KEY (listing_id) REFERENCES Auction_Listings (listing_id));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Bids LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Bids.csv')
        data.to_sql('Bids', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importTransactionsData()
Parameters: None
Purpose: Create Transactions table and import transaction data into database.
'''
def importTransactionsData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Transactions(transaction_id INT PRIMARY KEY, seller_email TEXT, listing_id INT, bidder_email TEXT, date TEXT, payment REAL, FOREIGN KEY (seller_email) REFERENCES Bids (seller_email), FOREIGN KEY (bidder_email) REFERENCES Bids (email), FOREIGN KEY (listing_id) REFERENCES Bids (listing_id), FOREIGN KEY (payment) REFERENCES Bids (bid_price));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Transactions LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Transactions.csv')
        data.to_sql('Transactions', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importRatingsData()
Parameters: None
Purpose: Create Ratings table and import ratings data into database.
'''
def importRatingsData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Ratings(bidder_email TEXT, seller_email TEXT, date TEXT, rating INT, rating_desc TEXT, PRIMARY KEY(bidder_email, seller_email, date), FOREIGN KEY (bidder_email) REFERENCES Bidders (email), FOREIGN KEY (seller_email) REFERENCES Sellers (email));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Ratings LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Ratings.csv')
        data.to_sql('Ratings', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importCreditCardsData()
Parameters: None
Purpose: Create Credit_Card table and import credit card data into database.
'''
def importCreditCardsData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Credit_Cards(credit_card_num TEXT PRIMARY KEY, card_type TEXT, expire_month INT, expire_year INT, security_code INT, owner_email TEXT, FOREIGN KEY (owner_email) REFERENCES Users (email));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Credit_Cards LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Credit_Cards.csv')
        data.to_sql('Credit_Cards', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importAddressData()
Parameters: None
Purpose: Create Address table and import Address data into database.
'''
def importAddressData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Address(address_id TEXT PRIMARY KEY, zipcode INT, street_num INT, street_name TEXT, FOREIGN KEY (zipcode) REFERENCES Zipcode_Info (zipcode));') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Address LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Address.csv')
        data.to_sql('Address', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importZipcodeData()
Parameters: None
Purpose: Create Zipcode_Info table and import zipcode data into database.
'''
def importZipcodeData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Zipcode_Info(zipcode INT PRIMARY KEY, city TEXT, state TEXT);') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Zipcode_Info LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Zipcode_Info.csv')
        data.to_sql('Zipcode_Info', connection, if_exists='append', index = False)
        connection.commit()


'''
Function Name: importCategoriesData()
Parameters: None
Purpose: Create Categories table and import categories data into database.
'''
def importCategoriesData():
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    connection.execute('CREATE TABLE IF NOT EXISTS Categories(category_name TEXT PRIMARY KEY, parent_category TEXT);') #Create table if it doesn't exist
    cursor.execute('SELECT * FROM Categories LIMIT 1')
    isEmpty = len(cursor.fetchall())
    if isEmpty == 0:
        data = pd.read_csv('/Users/Tejas/Desktop/Workspace/CMPSC_431W/LionAuction/dataset/Categories.csv')
        data.to_sql('Categories', connection, if_exists='append', index = False)
        connection.commit()































