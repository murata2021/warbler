"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

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


    # When you’re logged in, can you add a message as yourself?
    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    # When you’re logged in, can you delete a message as yourself?
    def test_delete_message(self):
        """Can use delete a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            new_message=Message(text="hello",user_id=self.testuser.id)
            db.session.add(new_message)
            db.session.commit()

            resp=c.post(f"/messages/{new_message.id}/delete")
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location,f"http://localhost/users/{self.testuser.id}")

            second_message=Message(text="hello22",user_id=self.testuser.id)
            db.session.add(second_message)
            db.session.commit()

            resp1=c.post(f"/messages/{second_message.id}/delete",follow_redirects=True)
            self.assertEqual(resp1.status_code, 200)
            html=resp1.get_data(as_text=True)

            self.assertNotIn("hello22",html)


    # When you’re logged out, are you prohibited from adding messages?
    def test_message_without_session(self):
        """Unauthorized access?"""

        with self.client as c1:
            # with c1.session_transaction() as sess:
            #     sess[CURR_USER_KEY] = 132222222222222222222222222222


            # import pdb; pdb.set_trace()
            resp1 = c1.post("/messages/new", data={"text": "Hello"},follow_redirects=True)
            html = resp1.get_data(as_text=True)            
            
            self.assertEqual(resp1.status_code, 200)  # Make sure it redirects
            self.assertIn("Access unauthorized", html)

            resp2 = c1.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp2.status_code, 302)  

    # When you’re logged out, are you prohibited from deleting messages?
    def test_delete_message_without_session(self):
        """Can use delete a message without login?"""
        with self.client as c:
            
            new_message=Message(text="hello",user_id=self.testuser.id)
            db.session.add(new_message)
            db.session.commit()

            resp=c.post(f"/messages/{new_message.id}/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location,f"http://localhost/")

            second_message=Message(text="hello22",user_id=self.testuser.id)
            db.session.add(second_message)
            db.session.commit()

            resp1=c.post(f"/messages/{second_message.id}/delete",follow_redirects=True)
            self.assertEqual(resp1.status_code, 200)



# When you’re logged in, are you prohibiting from deleting a message as another user?

def test_add_message_for_another_user(self):
        """Can use delete a message that doesn't belong to you?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message(
                id=10,
                text="a test message",
                user_id=self.testuser_id
            )
            db.session.add(m)
            db.session.commit()

            resp = c.post("/messages/10/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertEqual(m,Message.query.get(10))

            


        

