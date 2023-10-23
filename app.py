# this should perform the function of a REST API that allows for the addition of new stocks (name, symbol and price)
from flask import Flask, jsonify, request, Blueprint, render_template, redirect, url_for
import requests
from ariadne import ObjectType, QueryType, MutationType, make_executable_schema, load_schema_from_path
from graphql_server.flask import GraphQLView
import asyncio, websockets, random

#gql schema for db entities
type_defs = load_schema_from_path("stocks.gql")

# why would I name them anything different from 'mutation' and 'query'??
query = QueryType()
mutation = MutationType()


app = Flask(__name__)

site = Blueprint('site', __name__, template_folder='templates')
#look up if you have to define a template for what type of JSON it can accept
stocks = [
    {
    'id': 1,
    'name': 'sample',
    'symbol': 'SPL',
    'currentPrice': 2,
    'highestPrice': 5,
    'lowestPrice': 0    
    }
]


@app.route('/')
def home():
    return render_template('index.html', stocks=stocks)

#1.a: adding a new stock
@app.route('/', methods=['POST'])
def post_data():
    new_stock= {
        # new stocks will be appended to the list of current stocks
        'id': int(len(stocks) + 1),
        'name': request.form['name'],
        'symbol': request.form['symbol'],
        'currentPrice': float(request.form['currentPrice']),
        'highestPrice': float(request.form['highestPrice']),
        'lowestPrice': float(request.form['lowestPrice']),
    }
    stocks.append(new_stock)
    return jsonify({'stock': new_stock}), 201

# this is for 1.b: returning all stocks in the database
@app.route('/', methods=['GET'])
def get_all_stocks():
    return jsonify({'stocks': stocks})

#REST declarations
#################################################
#GRAPHQL declarations

#GraphQL function to retrieve a specific stock based on ID
@query.field("stock")
def resolve_stock(_, id):
    for stock in stocks:
        if stock["id"] == id:
            return jsonify(stock)
    return None
#maybe add a way to query based on the ticker symbol instead of ID?

@mutation.field("addStock")
def resolve_add_stock(_, name, symbol, currentPrice, highestPrice, lowestPrice):
    new_stock = {
        'id': len(stocks) + 1,
        'name': name,
        'symbol': symbol,
        'currentPrice': currentPrice,
        'highestPrice': highestPrice,
        'lowestPrice': lowestPrice
    }
    stocks.append(new_stock)
    return new_stock

#not sure how this works exactly, but it looks like it allows the gql schema to interact with the python methods I made?
schema = make_executable_schema(type_defs, query, mutation)

#this redirects the user to the 'graphiQL' ui thing. You have to add it to the end of the URL.
app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True))

if __name__ == '__main__':
    app.run(debug=True)