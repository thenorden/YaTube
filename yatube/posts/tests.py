from django.test import TestCase, Client


# Create your tests here.
from .models import User, Post


# class TestStringMethods(TestCase):
#     def test_length(self):
#         self.assertEqual(len('yatube'), 6)
#
#     def test_show_msg(self):
#         self.assertTrue(False, msg='Важная проверка')


# class TestProfile(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create(username='testprofile', email='test@test.com', password='1234')
#         self.post = Post.objects.create(text='testpost', author=self.user)
#
#     def test_profile(self):
#         response = self.client.get('/testprofile/')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context['posts']), 1)
#         self.assertIsInstance(response.context['profile'], User)
#         self.assertEqual(response.context['profile'].username, self.user.username)

# class TestProfile(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")
#         self.post = Post.objects.create(text='testpost', author=self.user)
#
#     def test_profile(self):
#         response = self.client.get('/sarah/')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.context['posts']), 1)
#         self.assertIsInstance(response.context['profile'], User)
#         self.assertEqual(response.context['profile'].username, self.user.username)
#
#
# class TestPost(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(username='testuser', email='testemail@test.com', password='test')
#         self.client = Client()
#         self.post = Post.objects.create(text='testtext', author=self.user)
#
#     def test_new_post(self):
#         path = f'/testuser/{self.post.id}'
#         response = self.client.get('/testuser/1')
#         self.assertEqual(response.status_code, 200)
