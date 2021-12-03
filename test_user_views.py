"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()
        app.config['TESTING'] = True

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    
# When you’re logged in, can you see the follower / following pages for any user?

    def test_user_follow_pages_loggedin(self):

        """Tests User will be able to see follow pages when he/she logged in"""

        with self.client as c:

            user=User.signup(username="testuser2",
                            email="test2@test2.com",
                            password="testuser2",
                            image_url=None)

            chicken_tender=User.signup(username="chicken_tenders",
                            email="chicken@tender.com",
                            password="123456",
                            image_url=None)

            db.session.commit()

            self.testuser.followers.append(chicken_tender)
            self.testuser.followers.append(user)

            self.testuser.following.append(user)
            
            db.session.commit()

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            #checks following page
            resp= c.get(f"/users/{sess[CURR_USER_KEY]}/following")            
            html=resp.get_data(as_text=True)
            self.assertIn("testuser2",html)
            self.assertEqual(resp.status_code, 200)
            
            #checks followers
            resp2= c.get(f"/users/{sess[CURR_USER_KEY]}/followers")
            html=resp2.get_data(as_text=True)
            self.assertIn("testuser2",html)
            self.assertIn("chicken_tenders",html)
            self.assertEqual(resp.status_code, 200)

    # When you’re logged out, are you disallowed from visiting a user’s follower / following pages?

    def test_user_follow_pages_not_loggedin(self):
        """Tests User will not  be able to see follow pages when he/she is not logged in"""

        with self.client as c:

            user=User.signup(username="testuser2",
                            email="test2@test2.com",
                            password="testuser2",
                            image_url=None)

            chicken_tender=User.signup(username="chicken_tenders",
                            email="chicken@tender.com",
                            password="123456",
                            image_url=None)

            db.session.commit()

            self.testuser.followers.append(chicken_tender)
            self.testuser.followers.append(user)

            self.testuser.following.append(user)
            
            db.session.commit()

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 132222222222222222222222222222222 #user does not exist!

            ######following page
            resp= c.get(f"/users/{sess[CURR_USER_KEY]}/following",follow_redirects=True)
            html = resp.get_data(as_text=True)            # Make sure it redirects
            self.assertIn("Access unauthorized", html)
            self.assertEqual(resp.status_code, 200)

            resp1= c.get(f"/users/{sess[CURR_USER_KEY]}/following")
            self.assertEqual(resp1.status_code, 302)  

            ######followers page
            resp3= c.get(f"/users/{sess[CURR_USER_KEY]}/followers",follow_redirects=True)
            html = resp3.get_data(as_text=True)            # Make sure it redirects
            self.assertIn("Access unauthorized", html)
            self.assertEqual(resp3.status_code, 200)

            resp4= c.get(f"/users/{sess[CURR_USER_KEY]}/followers")
            self.assertEqual(resp4.status_code, 302)  

    

