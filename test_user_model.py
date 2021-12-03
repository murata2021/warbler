"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User(
            email="test1@test1.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )

        user2 = User(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user3 = User(
            email="test3@test3.com",
            username="testuser3",
            password="HASHED_PASSWORD3"
        )
        users=[user1,user2,user3]

        db.session.add_all(users)
        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # Does the repr method work as expected?
        self.assertEqual(u.__repr__(),f"<User #{u.id}: {u.username}, {u.email}>")

    def test_follows(self):

        """Checks following and being followed"""

        user1 = User.query.filter(User.username=="testuser1").first()
        user2 = User.query.filter(User.username=="testuser2").first()
        user3 = User.query.filter(User.username=="testuser3").first()

        user1.following.append(user2)  #user 1 follows user 2
        user3.following.append(user1)  #user 3 follows user 1
        db.session.commit()

        # Does is_following successfully detect when user1 is following user2?
        self.assertEqual(user1.is_following(user2),True)
        self.assertEqual(user3.is_following(user1),True)

        # Does is_following successfully detect when user2 is not following user3 or him/herself?
        self.assertEqual(user2.is_following(user2),False)
        self.assertEqual(user2.is_following(user3),False)
        self.assertEqual(user1.is_following(user3),False)


        # Does is_followed_by successfully detect when user2 is followed by user1   ?
        self.assertEqual(user2.is_followed_by(user1),True)
        self.assertEqual(user1.is_followed_by(user3),True)


        #Does is_followed_by successfully detect when user1 is not followed by user2?
        self.assertEqual(user1.is_followed_by(user2),False)
        self.assertEqual(user1.is_followed_by(user1),False)

        # Does User.create successfully create a new user given valid credentials?

        new_user=User.signup(username="new_user",email="new_user@email.com",password="123456",image_url="")
        db.session.commit()

        self.assertEqual(new_user.id,User.query.filter(User.username=="new_user").first().id)

        # Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?

            #Checks username already exists
        new_user2=User.signup(username="new_user",email="new@gmail.com",password="123456",image_url="")
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        
        self.assertIsNone(new_user2.id)

            #Checks email already exists
        new_user3=User.signup(username="new_user1231231",email="new_user@email.com",password="123456",image_url="")
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        
        self.assertIsNone(new_user3.id)

    def test_authenticate(self):

        """Test authentication"""
        
        auth_user=User.signup(username="auth_user",email="aut_user@email.com",password="123456",image_url="")
        db.session.commit()
        # Does User.authenticate successfully return a user when given a valid username and password?

        self.assertEqual(auth_user,User.authenticate("auth_user","123456"))

        # Does User.authenticate fail to return a user when the username is invalid?
        self.assertEqual(False,User.authenticate("au_user","123456"))
        # Does User.authenticate fail to return a user when the password is invalid?
        self.assertEqual(False,User.authenticate("auth_user","12345678910"))

 


    