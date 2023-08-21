#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource, abort
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
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

api= Api(app)


class Scientists(Resource):
    def get(self):
        scientists = [s.to_dict(rules=("-missions",)) for s in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(**data)
        except:
            abort(400, errors=["validation errors"])
        db.session.add(new_scientist)
        db.session.commit()
        return make_response(new_scientist.to_dict(rules=("-missions",)), 201)

api.add_resource(Scientists, "/scientists")

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.get_or_404(id, description="Scientist not found").to_dict(rules=("-missions.planet.missions",))
        return make_response(scientist, 200)
    
    def patch(self, id):
        data = request.get_json()
        scientist = Scientist.query.get_or_404(id, description="Scientist not found")
        try:
            for attr, value in data.items():
                setattr(scientist, attr, value)
        except:
            abort(400, errors=["validation errors"])
        db.session.add(scientist)
        db.session.commit()
        return make_response(scientist.to_dict(rules=("-missions",)), 202)
    
    def delete(self, id):
        scientist = Scientist.query.get_or_404(id, description="Scientist not found")
        db.session.delete(scientist)
        db.session.commit()
        return make_response("", 204)
        

api.add_resource(ScientistById, "/scientists/<int:id>")

class Planets(Resource):
    def get(self):
        planets = [p.to_dict(rules=("-missions",)) for p in Planet.query.all()]
        return make_response(planets, 200)

api.add_resource(Planets, "/planets")

class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_mission = Mission(**data)
        except:
            abort(400, errors=["validation errors"])
        db.session.add(new_mission)
        db.session.commit()
        return make_response(new_mission.to_dict(rules=("-planet.missions", "-scientist.missions",)), 201)
    
api.add_resource(Missions, "/missions")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
