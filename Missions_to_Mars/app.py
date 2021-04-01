from flask_pymongo import PyMongo
from flask import Flask, render_template, redirect

#import the scrape_mars.py file
import scrape_mars

#MONGODB & CREATING FLASKS
#####################################################

#Creating a Flask

app = Flask(__name__)

#Connecting to PyMongo localhost & assigning variables
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars"
mongo = PyMongo(app)

#Route index.html using Mongo
@app.route('/')

def index():
	mars = mongo.db.collection.find_one()

	return render_template('index.html', mars=mars)

@app.route('/scrape')
def scrape():
	marsscrape = scrape_mars

	mongo.db.collection.update({}, marsscrape, upsert=True)
	return redirect("/", code=302)


if __name__ == '__main__':
    app.run(debug=True)