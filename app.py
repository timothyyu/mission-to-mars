#Imports
from flask import Flask, render_template
from flask import jsonify, redirect
from flask_pymongo import PyMongo
import pymongo
from splinter import Browser
import scrape_mars

#Create instance of Flask class for web app
app = Flask(__name__)

#Establish connection between Mongo and Flask
mongo=PyMongo(app) #Flask <--> PyMongo link 

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
db = client.mars_news_collection
collection = db.mars_news_collection

#Flask route declaration
@app.route('/')
def index():
	return ""
	#return render_template('index.html', mars=mars)

@app.route('/scrape')
def scrape():
	print("Data scrape start:\n")
	print("================================================================")

	mars = mongo.db.mars_news_collection
	mars_data = scrape_mars.scrape()
	mars.update(
		{},
		mars_data,
		upsert=True
	)

	print("================================================================")
	print("Data scrape end:\n")

	return redirect("http://localhost:5000/", code=302)
	

if __name__ == "__main__":
	app.run(debug=True)