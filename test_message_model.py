"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


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

class MessageModelTestCase(TestCase):
    """Test message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user=User.signup(username="testuser",email="testuser@gmail.com",password="123456",image_url="")
        db.session.commit()

        msg=Message(text="fist warble",user_id=user.id)
        db.session.add(msg)
        db.session.commit()

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""

        u=User.query.filter(User.username=="testuser").first()
        self.assertEqual(len(u.messages), 1)
        
        msg1=Message.query.first()

        self.assertEqual(len(msg1.user_likes), 0)

    
    def test_message_likes(self):
        """test message likes"""

        user2=User.signup(username="testuser22",email="testuser22@gmail.com",password="123456",image_url="")

        msg1=Message.query.first()

        self.assertEqual(len(msg1.user_likes), 0)
        user2.likes.append(msg1)
        db.session.commit()
        self.assertEqual(len(msg1.user_likes), 1)



