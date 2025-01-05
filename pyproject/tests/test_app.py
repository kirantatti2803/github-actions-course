import pytest
from app import index  # Assuming your Flask app is in a file called `app.py`

def test_index():
    assert index() == "Hello, World!"


'''
@pytest.fixture
def client():
    # This will create a test client for the app
    with index.test_client() as client:
        yield client  # This will allow us to use the client in the test

def test_hello_world(client):
    # Send a GET request to the / route
    response = client.get('/')
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Assert that the response data contains the expected text
    assert b'Hello, World!' in response.data
'''