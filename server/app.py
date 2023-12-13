#!/usr/bin/env python3

from models import db, Hotel, HotelCustomer, Customer
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
class AllHotels(Resource):
    def get(self):
        response_body = [hotel.to_dict(rules=('-hotel_customers',)) for hotel in Hotel.query.all()]
        
        return make_response(response_body, 200)
    
api.add_resource(AllHotels, '/hotels')

class HotelById(Resource):
    
    def get(self, id):
    
        hotel = Hotel.query.filter_by(id=id).first()

        if hotel:
            response_body = hotel.to_dict(rules=('-hotel_customers.hotel','-hotel_customers.customer'))
            return make_response(response_body, 200)
        else:
            response_body = {
                "error" : "Hotel not found"
                }
            return make_response(response_body, 404)
        

    def delete(self, id):

        hotel = Hotel.query.filter_by(id=id).first()

        if hotel:
            db.session.delete(hotel)
            db.session.commit()
            return make_response("", 204)
        else:
            response_body = {
                "error" : "Hotel not found"
                }
            return make_response(response_body, 404)
        
api.add_resource(HotelById, '/hotels/<int:id>')


class AllCustomers(Resource):
    def get(self):
        response_body = [custumer.to_dict(rules=('-hotel_customers',)) for custumer in Customer.query.all()]
        return make_response(response_body, 200)
    

api.add_resource(AllCustomers, '/customers')


class AllHotelCustomers(Resource):
    def post(self):
        try:
            new_hotel_customer = HotelCustomer(customer_id=request.json['customer_id'], hotel_id=request.json['hotel_id'], rating=request.json['rating'])
            db.session.add(new_hotel_customer)
            db.session.commit()
            response_body = new_hotel_customer.to_dict(rules=('-hotel.hotel_customers','-customer.hotel_customers', )) 
            return make_response(response_body, 201) 
        except:
            reponse_body = {"errors": ["validation errors"]}
            return make_response(reponse_body, 400)  

api.add_resource(AllHotelCustomers, '/hotel_customers')
            
@app.route('/')
def index():
    return '<h1>Mock Code challenge</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)
