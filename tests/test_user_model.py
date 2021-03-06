import unittest
import time
from datetime import datetime
from app.models import User, AnonymousUser, Role, Permission
from app import db, create_app


class UserModelTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_setter(self):
		u = User(password = 'cat')
		self.assertTrue(u.password_hash is not None)

	def test_no_password_getter(self):
		u = User(password = 'cat')
		with self.assertRaises(AttributeError):
			u.password

	def test_password_verification(self):
		u = User(password = 'cat')
		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))

	def test_password_salts_are_random(self):
		u1 = User(password = 'cat')
		u2 = User(password = 'cat')
		self.assertTrue(u1.password_hash != u2.password_hash)

	def test_valid_confirmation_token(self):
		u = User(password = 'password123')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token()
		self.assertTrue(u.confirm(token))

	def test_invalid_confirmation_token(self):
		u1= User(password = 'cat')
		u2 = User(password = 'cat')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		token = u1.generate_confirmation_token()
		self.assertFalse(u2.confirm(token))

	def test_expired_confirmation_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token(1)
		time.sleep(2)
		self.assertFalse(u.confirm(token))

	def test_roles_and_permissions(self):
		u = User(email = 'marco@example.com', password = 'cat')
		self.assertTrue(u.can(Permission.WRITE_ARTICLES))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))

	def test_timestamps(self):
		u = User(email = 'marcel@example.com', password = 'cat')
		db.session.add(u)
		db.session.commit()
		self.assertTrue((datetime.utcnow()- u.member_since).total_seconds() < 1)
		self.assertTrue((datetime.utcnow() - u.last_seen).total_seconds() < 1)

	def test_ping(self):
		u = User(email = 'mariana@example.com', password = 'cat')
		db.session.add(u)
		db.session.commit()
		previous_last_seen = u.last_seen
		#time.sleep(2)
		u.ping()
		self.assertTrue(previous_last_seen < u.last_seen)
	


