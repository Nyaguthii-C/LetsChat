import tempfile
from PIL import Image
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest
pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def make_user(**kwargs):
        return CustomUser.objects.create_user(
            email=kwargs.get('email', 'test@example.com'),
            full_name=kwargs.get('full_name', 'Test User'),
            password=kwargs.get('password', 'testpass123')
        )
    return make_user


@pytest.fixture
def auth_client(api_client, create_user):
    user = create_user()
    response = api_client.post(reverse('login'), {
        'email': user.email,
        'password': 'testpass123'
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client, user


def get_temp_image():
    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file, format='JPEG')
    tmp_file.seek(0)
    return SimpleUploadedFile(
        name='test.jpg',
        content=tmp_file.read(),
        content_type='image/jpeg'
    )


def test_register_user(api_client):
    url = reverse('register')
    image = get_temp_image()
    data = {
        'email': 'newuser@example.com',
        'full_name': 'New User',
        'password': 'password123',
        'profile_photo': image,
    }
    response = api_client.post(url, data, format='multipart')
    assert response.status_code == 201
    assert CustomUser.objects.filter(email='newuser@example.com').exists()


def test_login_user(api_client, create_user):
    user = create_user(email='login@example.com', password='testpass123')
    response = api_client.post(reverse('login'), {
        'email': user.email,
        'password': 'testpass123'
    })
    assert response.status_code == 200
    assert 'access' in response.data


def test_login_invalid_credentials(api_client):
    response = api_client.post(reverse('login'), {
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    })
    assert response.status_code == 400


def test_login_returns_token(api_client, create_user):
    user = create_user(
        email="tester@example.com",
        password="secret123"
    )
    url = reverse("login")
    response = api_client.post(url, {"email": "tester@example.com", "password": "secret123"})
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


def test_get_user_profile(auth_client):
    client, user = auth_client
    response = client.get(reverse('user-detail'))
    assert response.status_code == 200
    assert response.data['email'] == user.email


def test_update_user_profile(auth_client):
    client, user = auth_client
    new_image = get_temp_image()
    data = {
        'full_name': 'Updated Name',
        'password': 'newpass123',
        'profile_photo': new_image
    }
    response = client.put(reverse('user-detail'), data, format='multipart')
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.full_name == 'Updated Name'
    assert user.check_password('newpass123')


def test_delete_user(auth_client):
    client, user = auth_client
    response = client.delete(reverse('user-detail'))
    assert response.status_code == 204
    assert not CustomUser.objects.filter(id=user.id).exists()
