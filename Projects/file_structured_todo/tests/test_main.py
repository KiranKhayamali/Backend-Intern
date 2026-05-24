
import pytest
pytest.importorskip("aiosqlite")
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from ..main import app
from ..core.db.database import Base
from ..core.deps import get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome!! to the ToDo List....."}


def test_create_user(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "securepass123",
        "is_admin": False
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["is_admin"] is False
    assert "password" not in data


def test_create_duplicate_user(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "securepass123",
        "is_admin": False
    }
    response1 = client.post("/users/", json=user_data)
    assert response1.status_code == 201

    response2 = client.post("/users/", json=user_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


def test_create_user_missing_fields(client, setup_database):
    user_data = {"username": "testuser"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_get_all_users(client, setup_database):
    users = [
        {"username": "user1", "password": "pass1", "is_admin": False},
        {"username": "user2", "password": "pass2", "is_admin": True},
    ]
    for user in users:
        client.post("/users/", json=user)

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"
    assert data[1]["username"] == "user2"


def test_get_all_users_empty(client, setup_database):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


def test_login_success(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "securepass123",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "securepass123"
    }
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_username(client, setup_database):
    login_data = {
        "username": "nonexistent",
        "password": "somepass"
    }
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_invalid_password(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "correctpass",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "wrongpass"
    }
    response = client.post("/users/token", data=login_data)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_update_user(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "pass123",
        "is_admin": False
    }
    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    update_data = {
        "username": "updateduser",
        "is_admin": True
    }
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["is_admin"] is True


def test_update_nonexistent_user(client, setup_database):
    update_data = {
        "username": "newname",
        "is_admin": False
    }
    response = client.put("/users/999", json=update_data)
    assert response.status_code == 404


def test_create_note_authenticated(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "pass123"
    }
    login_response = client.post("/users/token", data=login_data)
    token = login_response.json()["access_token"]

    note_data = {
        "title": "My First Note",
        "memo": "This is a test note"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/notes/", json=note_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Note"
    assert data["memo"] == "This is a test note"
    assert data["user_id"] == 1


def test_create_note_unauthenticated(client, setup_database):
    note_data = {
        "title": "Unauthorized Note",
        "memo": "This should fail"
    }
    response = client.post("/notes/", json=note_data)
    assert response.status_code == 403


def test_get_all_notes(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "pass123"
    }
    login_response = client.post("/users/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    notes_data = [
        {"title": "Note 1", "memo": "Memo 1"},
        {"title": "Note 2", "memo": "Memo 2"},
    ]
    for note in notes_data:
        client.post("/notes/", json=note, headers=headers)

    response = client.get("/notes/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_note_by_id(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "pass123"
    }
    login_response = client.post("/users/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    note_data = {
        "title": "Test Note",
        "memo": "Test Memo"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers)
    note_id = create_response.json()["id"]

    response = client.get(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["memo"] == "Test Memo"


def test_get_nonexistent_note(client, setup_database):
    response = client.get("/notes/999")
    assert response.status_code == 404


def test_update_note_by_owner(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "pass123"
    }
    login_response = client.post("/users/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    note_data = {
        "title": "Original Title",
        "memo": "Original Memo"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers)
    note_id = create_response.json()["id"]

    update_data = {
        "title": "Updated Title",
        "memo": "Updated Memo"
    }
    response = client.put(f"/notes/{note_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["memo"] == "Updated Memo"


def test_update_note_unauthorized(client, setup_database):
    user1_data = {
        "username": "user1",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user1_data)

    login1_data = {
        "username": "user1",
        "password": "pass123"
    }
    login1_response = client.post("/users/token", data=login1_data)
    token1 = login1_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    note_data = {
        "title": "User1 Note",
        "memo": "User1 Memo"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers1)
    note_id = create_response.json()["id"]

    user2_data = {
        "username": "user2",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user2_data)

    login2_data = {
        "username": "user2",
        "password": "pass123"
    }
    login2_response = client.post("/users/token", data=login2_data)
    token2 = login2_response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    update_data = {
        "title": "Hacked Title",
        "memo": "Hacked Memo"
    }
    response = client.put(f"/notes/{note_id}", json=update_data, headers=headers2)
    assert response.status_code == 403
    assert "not the owner" in response.json()["detail"]


def test_update_note_by_admin(client, setup_database):
    user1_data = {
        "username": "user1",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user1_data)

    login1_data = {
        "username": "user1",
        "password": "pass123"
    }
    login1_response = client.post("/users/token", data=login1_data)
    token1 = login1_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    note_data = {
        "title": "User1 Note",
        "memo": "User1 Memo"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers1)
    note_id = create_response.json()["id"]

    admin_data = {
        "username": "admin",
        "password": "adminpass123",
        "is_admin": True
    }
    client.post("/users/", json=admin_data)

    admin_login_data = {
        "username": "admin",
        "password": "adminpass123"
    }
    admin_login_response = client.post("/users/token", data=admin_login_data)
    admin_token = admin_login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    update_data = {
        "title": "Admin Updated Title",
        "memo": "Admin Updated Memo"
    }
    response = client.put(f"/notes/{note_id}", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Admin Updated Title"


def test_delete_note_by_owner(client, setup_database):
    user_data = {
        "username": "testuser",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user_data)

    login_data = {
        "username": "testuser",
        "password": "pass123"
    }
    login_response = client.post("/users/token", data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    note_data = {
        "title": "Delete Me",
        "memo": "This will be deleted"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers)
    note_id = create_response.json()["id"]

    response = client.delete(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 200
    assert "successfully removed" in response.json()["message"]

    response = client.get(f"/notes/{note_id}", headers=headers)
    assert response.status_code == 404


def test_delete_note_unauthorized(client, setup_database):
    user1_data = {
        "username": "user1",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user1_data)

    login1_data = {
        "username": "user1",
        "password": "pass123"
    }
    login1_response = client.post("/users/token", data=login1_data)
    token1 = login1_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    note_data = {
        "title": "Protected Note",
        "memo": "User1 Memo"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers1)
    note_id = create_response.json()["id"]

    user2_data = {
        "username": "user2",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user2_data)

    login2_data = {
        "username": "user2",
        "password": "pass123"
    }
    login2_response = client.post("/users/token", data=login2_data)
    token2 = login2_response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    response = client.delete(f"/notes/{note_id}", headers=headers2)
    assert response.status_code == 403
    assert "not the owner" in response.json()["detail"]


def test_delete_note_by_admin(client, setup_database):
    user1_data = {
        "username": "user1",
        "password": "pass123",
        "is_admin": False
    }
    client.post("/users/", json=user1_data)

    login1_data = {
        "username": "user1",
        "password": "pass123"
    }
    login1_response = client.post("/users/token", data=login1_data)
    token1 = login1_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    note_data = {
        "title": "Admin Delete Test",
        "memo": "User1 Memo"
    }
    create_response = client.post("/notes/", json=note_data, headers=headers1)
    note_id = create_response.json()["id"]

    admin_data = {
        "username": "admin",
        "password": "adminpass123",
        "is_admin": True
    }
    client.post("/users/", json=admin_data)

    admin_login_data = {
        "username": "admin",
        "password": "adminpass123"
    }
    admin_login_response = client.post("/users/token", data=admin_login_data)
    admin_token = admin_login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.delete(f"/notes/{note_id}", headers=admin_headers)
    assert response.status_code == 200
    assert "successfully removed" in response.json()["message"]

