import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Movie, Actor

# To get the JWT 
casting_assistant_auth_header = {"Authorization": "Bearer {}".format(os.environ.get('ASSISTANT_TOKEN'))}
casting_director_auth_header = {"Authorization": "Bearer {}".format(os.environ.get('DIRECTOR_TOKEN'))}
executive_producer_auth_header = {"Authorization": "Bearer {}".format(os.environ.get('PRODUCER_TOKEN'))}

class CastingAgencyTestCase(unittest.TestCase):
    
    """This class represents Casting-Agency test case"""
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstonedb-test"
        self.database_path = "postgresql://{}@{}/{}".format('postgres','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_movie = {
            'name': 'Men In Black',
            'genre': 'Sci-fi'
        }
        self.new_actor = {
            'name': 'Diane Keaton',
            'gender': 'Female',
            'movie_id': 4
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # Test get:movies request by Casting-Assistant Role
    def test_get_movies(self):
        res = self.client().get('/movies', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    #Test get:movies request NOT FOUND by Casting Assistant Role
    def test_404_not_found_movies(self):
        res = self.client().get('/movies/100', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    # Test post:movies request by Executive Producer Role
    def test_create_new_movie(self):
        res = self.client().post('/movies',headers = executive_producer_auth_header, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    # Test post:movies is not allowed by Casting Director
    def test_401_create_movies_unauthorized(self):
        res = self.client().post('/movies', headers = casting_director_auth_header, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unauthorized')
    
    # Test patch:movies request by Executive Producer Role
    def test_update_movies(self):
        res = self.client().patch('/movies/2',headers = executive_producer_auth_header, json={'genre':'Action'})
        data = json.loads(res.data)
        movie = Movie.query.filter(Movie.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(movie.format()['genre'], 'Action')

    # Test patch:movies is not allowed by Casting Assistant
    def test_401_update_movies_unauthorized(self):
        res = self.client().patch('/movies/2', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unauthorized')

    # Test delete:movies request by Executive Producer Role
    def test_delete_movie(self):
        res = self.client().delete('/movies/6', headers = executive_producer_auth_header)
        data = json.loads(res.data)
        movie = Movie.query.filter(Movie.id == 6).one_or_none

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 6)
        self.assertEqual(movie, None)

    # Test delete:movies by Executive Producer Role if a movie does not exist
    def test_422_if_movie_does_not_exist(self):
        res = self.client().delete('movies/100', headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # Test get:actors request by Casting Assistant Role
    def test_get_actors(self):
        res = self.client().get('/actors', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # Test 404 if actor is not found by Casting Assistant Role
    def test_404_if_actor_not_found(self):
        res = self.client().get('/actors/100', headers = casting_assistant_auth_header)
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')
    
    # Test post:actors request by Casting Director Role
    def test_create_new_actor(self):
        res = self.client().post('/actors', headers = casting_director_auth_header, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    # Test 401 post:actors request not allowed by Casting Assistant Role
    def test_401_if_actors_creation_not_allowed(self):
        res = self.client().post('/actors/50', headers = casting_assistant_auth_header, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unauthorized')
    
    # Test patch:actors request by Casting Director Role
    def test_update_actors(self):
        res = self.client().patch('/actors/9',headers = casting_director_auth_header, json={'movie_id': 3})
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == 9).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(actor.format()['movie_id'], 3)

    # Test patch:actors not allowed by Casting Assistant
    def test_401_update_actors_unauthorized(self):
        res = self.client().patch('/actors/2', headers = casting_assistant_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unauthorized')

    # Test delete:actor request by Executive Producer Role
    def test_delete_actor(self):
        res = self.client().delete('/actors/9', headers = executive_producer_auth_header)
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == 9).one_or_none

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 9)
        self.assertEqual(actor, None)

    # Test delete:actors request by Executive Producer Role if delete an actor does not exist
    def test_422_if_actor_does_not_exist(self):
        res = self.client().delete('actors/100', headers = executive_producer_auth_header)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
