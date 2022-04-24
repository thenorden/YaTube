import tempfile

from django.test import TestCase, Client, override_settings

from django.urls import reverse

from .models import User, Post, Group


class InitTestMixin(TestCase):
    def setUp(self):
        username = "sarah"
        email = "connor.s@skynet.com"
        password = "12345"

        title = "TestGroup"
        slug = "newtest"
        description = "TestDesc"

        self.anonim_user = Client()
        self.client = Client()
        self.group = Group.objects.create(title=title, slug=slug, description=description)
        self.user = User.objects.create_user(username=username, email=email, password=password)
        self.client.force_login(self.user)


class ProfileTest(InitTestMixin, TestCase):
    def test_register_user(self):
        kwargs = {'username': self.user.username}
        response = self.client.get(reverse('profile', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)


class PostNewTest(InitTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(text='init_text', author=self.user)

    def test_auth_new_post(self):
        data = {'text': 'test_test', 'author': self.user}
        response = self.client.post(reverse('new_post'), data=data, follow=True)
        posts_list = [post.text for post in response.context['page']]
        self.assertTrue('test_test' in posts_list)

    def test_anonim_new_post(self):
        response = self.anonim_user.post(reverse('new_post'), follow=True)
        self.assertEqual([('/auth/login/?next=/new/', 302)], response.redirect_chain)

    def test_index_post(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.post.text)

    def test_profile_post(self):
        kwargs = {'username': self.user.username}
        response = self.client.get(reverse('profile', kwargs=kwargs))
        self.assertContains(response, self.post.text)

    def test_profile_view_post(self):
        kwargs = {'username': self.user.username, 'post_id': self.post.id}
        response = self.client.get(reverse('post', kwargs=kwargs))
        self.assertContains(response, self.post.text)


class PostEditTest(InitTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(text='init_text', author=self.user)
        self.edit_text = 'edit_text'
        kwargs = {'username': self.user.username, 'post_id': self.post.pk}
        data = {'text': self.edit_text}
        self.client.post(reverse('post_edit', kwargs=kwargs), data=data)

    def test_edit_index_post(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.edit_text)

    def test_edit_profile_post(self):
        kwargs = {'username': self.user.username}
        response = self.client.get(reverse('profile', kwargs=kwargs))
        self.assertContains(response, self.edit_text)

    def test_edit_profile_view_post(self):
        kwargs = {'username': self.user.username, 'post_id': self.post.id}
        response = self.client.get(reverse('post', kwargs=kwargs))
        self.assertContains(response, self.edit_text)


class ErrorsTest(InitTestMixin, TestCase):
    def setUp(self):
        super().setUp()

    def test_handler404(self):
        response = self.client.get('/something/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')


class ImageTest(InitTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                image = 'media/tests/test_image.jpg'
                txt = 'media/tests/test_txt.txt'
                with open(image, 'rb') as img, open(txt, 'rb') as txt:
                    data_image = {"text": "Test post", "image": img, "author": self.user, 'group': self.group.pk}
                    data_txt = {"text": "Test txt", "image": txt, "author": self.user, 'group': self.group.pk}
                    self.client.post(reverse('new_post'), data=data_image)
                    self.client.post(reverse('new_post'), data=data_txt)

    def test_image_index(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, '<img')

    def test_image_profile(self):
        kwargs = {'username': self.user.username}
        response = self.client.get(reverse('profile', kwargs=kwargs))
        self.assertContains(response, '<img')

    def test_image_group(self):
        kwargs = {'slug': self.group.slug}
        response = self.client.get(reverse('group', kwargs=kwargs))
        self.assertContains(response, '<img')

    def test_no_image(self):
        kwargs = {'username': self.user.username}
        response = self.client.get(reverse('profile', kwargs=kwargs))
        self.assertEqual(len(response.context['posts']), 1)
