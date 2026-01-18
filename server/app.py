#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Heroes(Resource):
    def get(self):
        heroes = []
        for hero in Hero.query.all():
            hero_dict = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            }
            heroes.append(hero_dict)
        return make_response(jsonify(heroes), 200)

api.add_resource(Heroes, '/heroes')


class HeroesId(Resource):
    
    def get(self, id):
        hero = Hero.query.filter(Hero.id == id).first()
        
        if hero:
            hero_dict = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "hero_powers": []
            }

            for hero_power in hero.hero_powers:
                power_dict = {
                    "id": hero_power.power.id,
                    "name": hero_power.power.name,
                    "description": hero_power.power.description
                }
                hero_dict["hero_powers"].append(power_dict)

            return make_response(jsonify(hero_dict), 200)
        else:
            return make_response(jsonify({"error": "Hero not found"}), 404)

api.add_resource(HeroesId, '/heroes/<int:id>')


class Powers(Resource):
    
    def get(self):
        powers = []
        
        for power in Power.query.all():
            power_dict = {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }
            powers.append(power_dict)
        return make_response(jsonify(powers), 200)

api.add_resource(Powers, '/powers')


class PowersId(Resource):
    
    def get(self, id):
        power = Power.query.filter(Power.id == id).first()
        
        if power:
            power_dict = {
                "id": power.id, 
                "name": power.name, 
                "description": power.description 
            }
            return make_response(jsonify(power_dict), 200)
        else:
            return make_response(jsonify({"error": "Power not found"}), 404)
    
    def patch(self, id):
        try:
            power = Power.query.filter(Power.id == id).first()
            
            if not power:
                return make_response(jsonify({"error": "Power not found"}), 404)
            
            data = request.get_json()
            for attr, value in data.items():
                setattr(power, attr, value)
                
            db.session.add(power)
            db.session.commit()
            
            power_dict = {
                "id": power.id, 
                "name": power.name, 
                "description": power.description 
            }
            
            return make_response(jsonify(power_dict), 200)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(PowersId, '/powers/<int:id>')


class HeroPowersResource(Resource):
    
    def post(self):
        try:
            data = request.get_json()
            new_hero_power = HeroPower(
                strength=data.get('strength'),
                power_id=data.get('power_id'),
                hero_id=data.get('hero_id')
            )
            db.session.add(new_hero_power)
            db.session.commit()
            
            hero_power_dict = {
                "id": new_hero_power.id,
                "strength": new_hero_power.strength,
                "hero_id": new_hero_power.hero_id,
                "power_id": new_hero_power.power_id,
                "hero": {
                    "id": new_hero_power.hero.id,
                    "name": new_hero_power.hero.name,
                    "super_name": new_hero_power.hero.super_name
                },
                "power": {
                    "id": new_hero_power.power_id,
                    "name": new_hero_power.power.name,
                    "description": new_hero_power.power.description
                }
            }
            return make_response(jsonify(hero_power_dict), 200)
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(HeroPowersResource, '/hero_powers')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
