from django.test import TestCase, Client
from pathlib import Path

from .models import User, Post, Group


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")

    def test_register_user(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)


class PostNewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.login(username='sarah', password='12345')
        self.anonim_user = Client()
        self.post = Post.objects.create(text='init_text', author=self.user)

    def test_auth_new_post(self):
        response = self.client.post('/new/', {'text': 'test_test', 'author': self.user}, follow=True)
        posts_list = [post.text for post in response.context['page']]
        self.assertTrue('test_test' in posts_list)

    def test_anonim_new_post(self):
        response = self.anonim_user.post('/new/', follow=True)
        self.assertEqual([('/auth/login/?next=/new/', 302)], response.redirect_chain)

    def test_index_post(self):
        response = self.client.get('')
        self.assertContains(response, self.post.text)

    def test_profile_post(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, self.post.text)

    def test_profile_view_post(self):
        response = self.client.get(f'/{self.user.username}/{ self.post.id }/')
        self.assertContains(response, self.post.text)


class PostEditTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.login(username='sarah', password='12345')
        self.anonim_user = Client()
        self.post = Post.objects.create(text='init_text', author=self.user)
        self.edit_text = 'edit_text'
        self.client.post(f'/{self.user.username}/{self.post.pk}/edit/', {'text': self.edit_text})

    def test_edit_index_post(self):
        response = self.client.get('')
        self.assertContains(response, self.edit_text)

    def test_edit_profile_post(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, self.edit_text)

    def test_edit_profile_view_post(self):
        response = self.client.get(f'/{self.user.username}/{self.post.id}/')
        self.assertContains(response, self.edit_text)


class ErrorsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_handler404(self):
        response = self.client.get('/something/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')


class ImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="sarah", email="connor.s@skynet.com", password="12345")
        self.client.login(username='sarah', password='12345')
        self.group = Group.objects.create(title="TestGroup", slug="newtest", description="TestDesc")
        with open('media/posts/file.jpg', 'rb') as fp:
            self.client.post("/new/", {"text": "Test post", "image": fp, "author": self.user, 'group': self.group.pk})

    def test_image_index(self):
        response = self.client.get('')
        self.assertContains(response, '<img')

    def test_image_profile(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, '<img')

    def test_image_group(self):
        response = self.client.get(f'/group/{self.group.slug}/')
        self.assertContains(response, '<img')

    def test_no_image(self):
        with open('media/posts/onlytest.txt', 'rb') as fp:
            self.client.post("/new/", {"text": "Test post", "image": fp, "author": self.user, 'group': self.group.pk})
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(len(response.context['posts']), 1)
