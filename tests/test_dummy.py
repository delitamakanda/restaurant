import pytest
from django.urls import reverse


def test_dummy():
    """dummy test"""
    assert True


@pytest.mark.django_db
def test_hello_view(client):
    """Test hello view"""
    url = reverse("hello")
    response = client.get(url)
    assert response.status_code == 200
    assert response.content == b"Hello world"
