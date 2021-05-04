import datetime
import unittest
from unittest.mock import patch
from test_helpers import LoginTestCase

# add path to import app
import sys

sys.path.append("./")
from app import db
from app.models import Dataset, Task, Session


class TestGetSessions(LoginTestCase):
    """Tests for /api/sessions route to list and query sessions."""

    def create_sessions(self):
        # define datasets
        self.timestamp = datetime.datetime.utcnow()
        self.session_user_1 = Session(user_id=1, name="test", created_utc=self.timestamp)
        self.session_user_1_2 = Session(user_id=1, name="test2", created_utc=self.timestamp)
        self.session_user_2 = Session(user_id=2, name="test3", created_utc=self.timestamp)

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/sessions/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_no_sessions_returns_empty(self):
        """No sessions exist, return value is empty"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get sessions
        response = self.client.get(
            "/api/sessions/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) == 0)

    def test_single_owned_session_is_returned_correctly(self):
        """No sessions exist, return value is empty"""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add(self.session_user_1)
        db.session.commit()
        # get sessions
        response = self.client.get(
            "/api/sessions/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.session_user_1.to_json()])

    def test_multiple_owned_session_are_returned_correctly(self):
        """No sessions exist, return value is empty"""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add_all([self.session_user_1, self.session_user_1_2])
        db.session.commit()
        # get sessions
        response = self.client.get(
            "/api/sessions/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.session_user_1.to_json(), self.session_user_1_2.to_json()])

    def test_only_owned_sessions_are_returned(self):
        """No sessions exist, return value is empty"""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add_all([self.session_user_1, self.session_user_2])
        db.session.commit()
        # get sessions
        response = self.client.get(
            "/api/sessions/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.session_user_1.to_json()])

class TestGetSessionWithID(LoginTestCase):
    """Tests for /api/sessions/<id> route to list and query sessions."""

    def create_sessions(self):
        # define datasets
        self.timestamp = datetime.datetime.utcnow()
        self.session_user_1 = Session(user_id=1, name="test", created_utc=self.timestamp)
        self.session_user_1_2 = Session(user_id=1, name="test2", created_utc=self.timestamp)
        self.session_user_2 = Session(user_id=2, name="test3", created_utc=self.timestamp)

    def test_no_auth(self):
        """No authentication provided, response should be 401"""
        # protected route
        response = self.client.get("/api/sessions/1/", content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_session_does_not_exist(self):
        """No authentication provided, response should be 401"""
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # get session
        response = self.client.get(
            "/api/sessions/10/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_session_is_not_owned(self):
        """Session is not owned, response whould be 403."""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add(self.session_user_2)
        db.session.commit()
        # get session
        response = self.client.get(
            "/api/sessions/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_owned_session_returned_correctly(self):
        """Tests whether owned session is returned correctly"""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add(self.session_user_1)
        db.session.commit()
        # get session
        response = self.client.get(
            "/api/sessions/1/",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.session_user_1.to_json())

    def test_unowned_session_is_returned_correctly_with_session_token(self):
        """Session is not owned, but correcte session token is provided."""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add_all([self.session_user_1, self.session_user_2])
        db.session.commit()
        # create session token
        token = self.session_user_2.generate_session_token()
        # get session
        response = self.client.get(
            f"/api/sessions/2/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.session_user_2.to_json())

    def test_unowned_session_is_not_returned_with_invalid_session_token(self):
        """Session is not owned, but correcte session token is provided."""
        self.create_sessions()
        # authenticate
        token = self.add_and_authenticate("test", "asdf")
        # create token header
        token_headers = self.get_token_header(token)
        # add session data
        db.session.add_all([self.session_user_1, self.session_user_2])
        db.session.commit()
        # create session token
        token = "IamABadToken"
        # get session
        response = self.client.get(
            f"/api/sessions/2/?sessionToken={token}",
            headers=token_headers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)



if __name__ == "__main__":
    res = unittest.main(verbosity=3, exit=False)
