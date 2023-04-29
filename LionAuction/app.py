from flask import Flask, render_template, request
import sqlite3 as sql
import pandas as pd
import hashlib
import random

import urllib
from data import importSellerData, importUsersData, importVendorData, importBiddersData, importAddressData, importAuctionListingsData, importBidsData, importCategoriesData, importCreditCardsData, importHelpDeskData, importRatingsData, importTransactionsData, importZipcodeData, importRequestsData
app = Flask(__name__)
#Location of Host Server
host = 'http://127.0.0.1:5000/'
user = None
user_email = None
role = None
local_vendor = None
all_categories = []
curr_item = None


'''
Function Name: login()
Parameters: None
Purpose: log into corresponding homepage (Bidder, Seller, HelpDesk)
'''
@app.route('/', methods=['POST', 'GET'])
def login():
    importUsersData()
    importBiddersData()
    importSellerData()
    importVendorData()
    importHelpDeskData()
    importAuctionListingsData()
    importBidsData()
    importAddressData()
    importCategoriesData()
    importCreditCardsData()
    importRatingsData()
    importTransactionsData()
    importZipcodeData()
    importRequestsData()
    error = None
    if request.method == 'POST': 
        username = request.form['uname']
        password = request.form['psw']
        user = request.form['user']
        #print("username is " + username + " and password is " + password)
        result = valid_user(username, password, user)
        #print(result)
        if result == None:
            error = "Invalid Username, Password, and User Type"
        elif result[0] == username:
            global all_categories, user_email, role, local_vendor
            if user == "Bidders":
                query = "SELECT category_name FROM Categories WHERE parent_category = 'Root';"
                root = sqlite_data_to_list_of_dicts(query)
                root_categories = []
                for parent in root:
                    root_categories.append(parent["category_name"])
                categories = [["Root", root_categories]]
                for c in root_categories:
                    get_all_categories(c, categories)
                #print(categories)
                all_categories = categories
                user_email = username
                role = user
                #print(all_categories)
                #print(all_categories[0][1])
                return render_template('bidder_home.html', name=get_name(username), categories=all_categories)
            elif user == "Sellers":
                query = "SELECT category_name FROM Categories WHERE parent_category = 'Root';"
                root = sqlite_data_to_list_of_dicts(query)
                root_categories = []
                for parent in root:
                    root_categories.append(parent["category_name"])
                categories = [["Root", root_categories]]
                for c in root_categories:
                    get_all_categories(c, categories)
                #print(categories)
                all_categories = categories
                user_email = username
                role = user
                query = "SELECT * FROM Local_Vendors WHERE email = '{}';"
                vendor = sqlite_data_to_list_of_dicts(query.format(user_email))
                if vendor:
                    local_vendor = 1
                else:
                    local_vendor = 0
                return render_template('seller_home.html', name=get_email(username))
            elif user == "HelpDesk":
                user_email = username
                role = user
                return render_template('helpdesk_home.html', name=user)
    return render_template('login.html', error=error) #Renders login page



'''
Function Name: categories()
Parameters: None
Purpose: Used to dynamically query the catagories from the Catagories database along with their respectful subcatagories. Renders the catagories html page
'''
@app.route('/categories', methods=['POST', 'GET'])
def categories():
    if request.method == 'POST': 
        action = request.form['action']
        if action == "category":
            c = request.form['input']
            query = "SELECT category_name FROM Categories WHERE parent_category = '{}';"
            result = sqlite_data_to_list_of_dicts(query.format(c))
            res = []
            for cat in result:
                res.append(cat["category_name"])
            return render_template('categories.html', name=user, result=res, categories=all_categories)
        else:
            c = request.form['input']
            query = "SELECT * FROM Auction_Listings WHERE category = '{}' AND status = 1;"
            result = sqlite_data_to_list_of_dicts(query.format(c))
            return render_template('listings.html', name=user, result=result, categories=all_categories, parent=c)
    else:
        query = "SELECT category_name FROM Categories WHERE parent_category = 'Root';"
        root = sqlite_data_to_list_of_dicts(query)
        root_categories = []
        for parent in root:
            root_categories.append(parent["category_name"])
        return render_template('categories.html', name=user, result=root_categories, categories=all_categories)



'''
Function Name: local_vendors()
Parameters: None
Purpose: renders the local vendors html file, and sends back a list of vendors
'''
@app.route('/local_vendors', methods=['POST', 'GET'])
def local_vendors():
    return render_template('local_vendors.html', vendors=get_all_vendors(), name=user, categories=all_categories)



'''
Function Name: home()
Parameters: None
Purpose: Navigate to home page, used in header
'''
@app.route('/home', methods=['POST', 'GET']) #FIX THIS FUNCTION
def home():
    if role == "Bidders":
        return render_template('bidder_home.html', name=user, categories=all_categories)
    elif role == "Sellers":
        return render_template('seller_home.html', name=user)
    elif role == "HelpDesk":
        return render_template('helpdesk_home.html', name=user)


'''
Function Name: listings()
Parameters: None
Purpose: Displays seller's listings when seller is logged in
'''
@app.route('/listings', methods=['POST', 'GET'])
def listings():
    if role == "Bidders":
        return render_template('listings.html', name=user, categories=all_categories)
    elif role == "Sellers":
        query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}' AND status = 1;"
        active = sqlite_data_to_list_of_dicts(query.format(user))
        #active = list(active[0].values())
        query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}' AND status = 0;"
        inactive = sqlite_data_to_list_of_dicts(query.format(user))
        #inactive = list(inactive[0].values())
        query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}' AND status = 2;"
        sold = sqlite_data_to_list_of_dicts(query.format(user))
        #sold = list(sold[0].values())
        return render_template('my_listings.html', name=user, active=active, inactive=inactive, sold=sold)



'''
Function Name: account_info()
Parameters: None
Purpose: Returns corresponding account info of user and displays it on account_info.html
'''
@app.route('/account', methods=['POST', 'GET'])
def account_info():
    if request.method == "GET":
        if role == "Bidders":
            query = "SELECT email, first_name, last_name, gender, age, major, address_id, Address.zipcode, street_num, street_name, city, state, credit_card_num, card_type, expire_month, expire_year, security_code FROM {}, Address, Zipcode_Info, Credit_Cards WHERE email = '{}' AND Address.address_id = home_address_id AND Address.zipcode = Zipcode_Info.zipcode AND owner_email = '{}';"
            account_info = sqlite_data_to_list_of_dicts(query.format(role, user_email, user_email))
            account = list(account_info[0].values())
            card_length = len(account[12])
            account[12] = account[12][card_length - 4:]
            print(account)
            return render_template('account_info.html', name=user, categories=all_categories, account=account, role=role)
        elif role == "Sellers":
            if local_vendor == 0: #Seller but not a vendor
                query = "SELECT * FROM Sellers WHERE email = '{}';"
                account_info = sqlite_data_to_list_of_dicts(query.format(user_email))
                account = list(account_info[0].values())
                print(account)
                return render_template('account_info.html', name=user, account=account, role=role, local_vendor=local_vendor)
            else: #Seller but a vendor
                query = "SELECT Sellers.email, bank_routing_number, bank_account_number, balance, business_name, customer_service_phone_number, Address.zipcode, street_num, street_name, city, state FROM Sellers, Local_Vendors, Address, Zipcode_Info WHERE Sellers.email = '{}' AND Address.address_id = business_address_id AND Address.zipcode = Zipcode_Info.zipcode;"
                account_info = sqlite_data_to_list_of_dicts(query.format(user_email))
                account = list(account_info[0].values())
                print(account)
                return render_template('account_info.html', name=user, account=account, role=role, local_vendor=local_vendor)
            


'''
Function Name: update_account_info()
Parameters: None
Purpose: Returns corresponding account info of user and displays it on update_account.html so that it can be updated
'''
@app.route('/update_account', methods=['POST', 'GET'])
def update_account_info(): 
    if request.method == "GET":
        if role == "Bidders":
            query = "SELECT email, first_name, last_name, gender, age, major, address_id, Address.zipcode, street_num, street_name, city, state, credit_card_num, card_type, expire_month, expire_year, security_code FROM {}, Address, Zipcode_Info, Credit_Cards WHERE email = '{}' AND Address.address_id = home_address_id AND Address.zipcode = Zipcode_Info.zipcode AND owner_email = '{}';"
            account_info = sqlite_data_to_list_of_dicts(query.format(role, user_email, user_email))
            account = list(account_info[0].values())
            return render_template('update_account.html', name=user, categories=all_categories, account=account)
    else:
        if role == "Bidders":
            fname = request.form['fname']
            lname = request.form['lname']
            gender = request.form['gender']
            age = request.form['age']
            major = request.form['major']
            query = "UPDATE Bidders SET first_name = '{}', last_name = '{}', gender = '{}', age = {}, major = '{}' WHERE email = '{}';"
            update_data(query.format(fname, lname, gender, age, major, user_email))

            #Navigating back to account info page

            query = "SELECT email, first_name, last_name, gender, age, major, address_id, Address.zipcode, street_num, street_name, city, state, credit_card_num, card_type, expire_month, expire_year, security_code FROM {}, Address, Zipcode_Info, Credit_Cards WHERE email = '{}' AND Address.address_id = home_address_id AND Address.zipcode = Zipcode_Info.zipcode AND owner_email = '{}';"
            account_info = sqlite_data_to_list_of_dicts(query.format(role, user_email, user_email))
            print(account_info)
            account = list(account_info[0].values())
            card_length = len(account[12])
            account[12] = account[12][card_length - 4:]
            print(account)
            return render_template('account_info.html', name=user, categories=all_categories, account=account)




'''
Function Name: update_item_info()
Parameters: None
Purpose: Updates listing information
'''
@app.route('/update_item', methods=['POST', 'GET'])
def update_item_info():
    global curr_item
    if request.method == "GET":
        query = "SELECT category_name FROM Categories;"
        categories = sqlite_data_to_list_of_dicts(query)
        print(categories)
        cat = []
        for c in categories:
            cat.append(c['category_name'])
        return render_template('update_item.html', name=user, item=curr_item, role=role, categories=cat)
    else:
        lid = request.form['lid']
        auction_title = request.form['auction_title']
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        quantity = request.form['quantity']
        status = request.form['status']
        reserve_price = request.form['reserve_price']
        max_bids = request.form['max_bids']
        query = "UPDATE Auction_Listings SET category = '{}', auction_title = '{}', product_name = '{}', product_description = '{}', quantity = {}, reserve_price = '{}', max_bids = {}, status = {} WHERE listing_id = {} AND seller_email = '{}';"
        update_data(query.format(category, auction_title, name, description, quantity, reserve_price, max_bids, status, lid, user_email))
        
        query = "SELECT * FROM Auction_Listings WHERE listing_id = {};"
        item = sqlite_data_to_list_of_dicts(query.format(lid))
        item = list(item[0].values())
        curr_item = item
        return render_template('item.html', name=user, item=item, role=role)




'''
Function Name: add_listing()
Parameters: None
Purpose: Adds a new listing to the auction listing table. Ensures no repeat of listing_id is allowed
'''
@app.route('/add_listing', methods=['POST', 'GET'])
def add_listing():
    if request.method == "GET":
        query = "SELECT category_name FROM Categories;"
        categories = sqlite_data_to_list_of_dicts(query)
        print(categories)
        cat = []
        for c in categories:
            cat.append(c['category_name'])
        print(cat)
        return render_template('add_listing.html', name=user, item=curr_item, role=role, categories=cat)
    else:
        auction_title = request.form['auction_title']
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        quantity = request.form['quantity']
        status = request.form['status']
        reserve_price = request.form['reserve_price']
        max_bids = request.form['max_bids']
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        #CHOOSE RANDOM NUMBER FOR LID
        
        while(True):
            lid = random.randint(0,5000)
            cursor.execute("SELECT * FROM Auction_Listings WHERE listing_id = {};".format(lid))
            listing_ids = cursor.fetchall()
            if listing_ids == []:
                cursor.execute("INSERT INTO Auction_Listings(seller_email, listing_id, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, status) VALUES (?,?,?,?,?,?,?,?,?,?);", (user_email, lid, category, auction_title, name, description, quantity, reserve_price, max_bids, status)),
                connection.commit()
                connection.close()
                query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}' AND status = 1;"
                active = sqlite_data_to_list_of_dicts(query.format(user))
                #active = list(active[0].values())
                query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}' AND status = 0;"
                inactive = sqlite_data_to_list_of_dicts(query.format(user))
                #inactive = list(inactive[0].values())
                query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}' AND status = 2;"
                sold = sqlite_data_to_list_of_dicts(query.format(user))
                #sold = list(sold[0].values())
                return render_template('my_listings.html', name=user, active=active, inactive=inactive, sold=sold)
        


'''
Function Name: delete_listing_table()
Parameters: None
Purpose: Deletes a listing from the auction listing table. When deleting, user is prompted with a reason textfield to fill out. 
After it has been deleted, the listing data is moved to the Records table, where it will be stored along with the reason.
'''
@app.route('/delete_listing', methods=['POST', 'GET'])
def delete_listing_table():
    if request.method == "GET":
        query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}';"
        all_listings = sqlite_data_to_list_of_dicts(query.format(user_email))
        return render_template('delete_listing.html', name=user, listings=all_listings)
    else:
        lid = request.form['lid']
        reason = request.form['reason']
        query = "SELECT * FROM Auction_Listings WHERE listing_id = '{}';"
        item = sqlite_data_to_list_of_dicts(query.format(lid))
        item = list(item[0].values())

        query = "DELETE FROM Auction_Listings WHERE listing_id = '{}' AND seller_email = '{}';"
        update_data(query.format(lid, user_email))

        update_data('CREATE TABLE IF NOT EXISTS Records(seller_email TEXT, listing_id INT, category TEXT, auction_title TEXT, product_name TEXT, product_description TEXT, quantity INT, reserve_price REAL, max_bids INT, status INT, reason TEXT, PRIMARY KEY(seller_email, listing_id), FOREIGN KEY (seller_email) REFERENCES Sellers (email), FOREIGN KEY (category) REFERENCES Categories (category_name));') #Create table if it doesn't exist *Might have to make a join between Bidders and Sellers
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO Records(seller_email, listing_id, category, auction_title, product_name, product_description, quantity, reserve_price, max_bids, status, reason) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], reason))
        connection.commit()
        connection.close()
        
        query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}';"
        all_listings = sqlite_data_to_list_of_dicts(query.format(user_email))
        return render_template('delete_listing.html', name=user, listings=all_listings)


'''
Function Name: delete_listing(data)
Parameters: None
Purpose: Used to assist in collecting data from the table displayed in the frontend
'''
@app.route('/delete_listing/<data>', methods=['POST', 'GET'])
def delete_listing(data):
    if request.method == 'GET':
        decoded_data = urllib.parse.unquote(data)
        query = "SELECT * FROM Auction_Listings WHERE listing_id = '{}' AND seller_email = '{}';"
        item = sqlite_data_to_list_of_dicts(query.format(decoded_data, user_email))
        global curr_item
        item = list(item[0].values())
        curr_item = item
        query = "SELECT * FROM Auction_Listings WHERE seller_email = '{}';"
        all_listings = sqlite_data_to_list_of_dicts(query.format(user_email))
        return render_template('delete_listing.html', name=user, item=item, role=role, listings=all_listings, message="Reason for deleting listing:")
    


@app.route('/item/<data>', methods=['POST', 'GET'])
def item(data):
    if request.method == 'GET':
        decoded_data = urllib.parse.unquote(data)
        query = "SELECT * FROM Auction_Listings WHERE listing_id = '{}';"
        item = sqlite_data_to_list_of_dicts(query.format(decoded_data))
        
        if role == "Sellers":
            global curr_item
            item = list(item[0].values())
            curr_item = item
        return render_template('item.html', name=user, categories=all_categories, item=item, role=role)
    else:
        bid_amount = request.form("bidAmount")
        print(bid_amount)





#Database Manipulation Functions



'''
Function Name: valid_user()
Parameters: username, password
Purpose: verify credentials and role with users database and corresponding role database.
'''
def valid_user(username, password, user):
    connection = sql.connect('database.db')
    cursor = connection.cursor()
    pw = hashlib.sha256(password.encode())
    pw = pw.hexdigest()
    cursor = connection.execute("SELECT * FROM Users INNER JOIN " + user + " ON Users.email = " + user + ".email WHERE Users.email='" + username + "' AND password='" + pw + "';") #Returns email after checking if username and pasword are same
    return cursor.fetchone()



'''
Function Name: get_name()
Parameters: email
Purpose: make homepage personalized with welcome message.
'''
def get_name(username):
    query = "SELECT first_name FROM Bidders WHERE email='" + username + "';"
    global user
    d = sqlite_data_to_list_of_dicts(query)
    user = d[0]["first_name"]
    return user


'''
Function Name: get_email()
Parameters: email
Purpose: gets email of specific uyser
'''
def get_email(username):
    query = "SELECT email FROM Sellers WHERE email='" + username + "';"
    global user
    d = sqlite_data_to_list_of_dicts(query)
    user = d[0]["email"]
    return user

'''
Function Name: get_all_users()
Parameters: 
Purpose: returns all users
'''
def get_all_users():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM Users;') #All rows in the table
    return cursor.fetchall()


'''
Function Name: get_all_vendors()
Parameters: 
Purpose: returns all vendors
'''
def get_all_vendors():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT business_name, customer_service_phone_number FROM Local_Vendors ORDER BY business_name ASC')
    return cursor.fetchall()

'''Returns data from an SQL query as a list of dicts.'''
def sqlite_data_to_list_of_dicts(query):
    try:
        connection = sql.connect('database.db')
        connection.row_factory = sql.Row
        things = connection.execute(query).fetchall()
        unpacked = [{k: item[k] for k in item.keys()} for item in things]
        return unpacked
    except Exception as e:
        print(f"Failed to execute. Query: {query}\n with error:\n{e}")
        return []
    finally:
        connection.close()


'''
Function Name: update_data(query) 
Parameters: 
Purpose: Updates the database with any query such as insert, update, and delete
'''
def update_data(query):
    try:
        connection = sql.connect('database.db')
        cursor = connection.cursor()
        cursor.execute((query))
        connection.commit()
    except Exception as e:
        print(f"Failed to execute. Query: {query}\n with error:\n{e}")
    finally:
        connection.close()


'''Recursive function that gets stores all the categories and corresponding sub categories in a provided list'''
def get_all_categories(parent_category, list):
    sub_categories = get_sub_categories(parent_category)
    if sub_categories == []:
        return
    else:
        subs = []
        for s in sub_categories:
            subs.append(s["category_name"])
        list.append([parent_category, subs])
        for category in sub_categories:
            get_all_categories(category["category_name"], list)


'''Returns Sub Categories of the Parent Category given'''
def get_sub_categories(parent_category):
    query = "SELECT category_name FROM Categories WHERE parent_category = '{}';".format(parent_category)
    return sqlite_data_to_list_of_dicts(query) #e.g. [{'category_name': 'Beauty Products'}, {'category_name': 'Clothing'}]




if __name__ == "__main__":
    app.run()


