from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
client = TestClient(app)


@app.get("/")
def root():
    return {"message": "Hello World!"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200 
    assert response.json() == {"message": "Hello World!"}