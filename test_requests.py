import requests

heroku_url = "https://nigel-c0b396b99759.herokuapp.com"

#Tests that the index route works
def test_index_route():
    response = requests.get(f"{heroku_url}/")
    assert response.status_code == 200
    assert response.text == "Hello this is the main page"

#Tests that the testing route works
def test_testing_route():
    response = requests.get(f"{heroku_url}/testing")
    assert response.status_code == 200
    assert response.text == "Hello this is a test"