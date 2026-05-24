import pytest


from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from Projects.CafePOS.Backend.src.app.models.users import User


async def _fake_admin_user():
    return User(
        first_name="Admin",
        middle_name="",
        last_name="User",
        contact_number="9876543210",
        is_admin=True,
        role="waiter",
        hashed_password="password123"
    )


async def _fake_non_admin_user():
    return User(
        first_name="Regular",
        middle_name="",
        last_name="User",
        contact_number="0987654321",
        is_admin=False,
        role="waiter",
        hashed_password="password123"
    )


TEST_USER = {
    "first_name": "Test",
    "middle_name": "",
    "last_name": "User",
    "contact_number": "9876543210",
    "is_admin": False,
    "role": "waiter",
    "password": "password123"
}



@pytest.mark.asyncio
async def test_login(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        response = await client.post("/users/login", data={"username": test_user["contact_number"], "password": test_user["password"]})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_login_invalid_contact_number(client):
    response = await client.post("/users/login", data={"username": "invalid", "password": "password123"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found!"


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        response = await client.post("/users/login", data={"username": test_user["contact_number"], "password": "wrongpassword"})
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect password!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_login_unregistered_contact_number(client):
    response = await client.post("/users/login", data={"username": "0000000000", "password": "password123"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found!"


@pytest.mark.asyncio
async def test_login_sets_cookies(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        login_response = await client.post("/users/login", data={"username": test_user["contact_number"], "password": test_user["password"]})
        assert login_response.status_code == 200

        cookies = login_response.cookies
        assert "access_token" in cookies
        access_token_from_body = login_response.json()["access_token"]
        assert cookies.get("access_token") == access_token_from_body
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_refresh_token(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_reponse = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_reponse.status_code == 201
        login_response = await client.post("/users/login", data={"username": test_user["contact_number"], "password": test_user["password"]})
        assert login_response.status_code == 200

        client.cookies.set("refresh_token", login_response.json()["refresh_token"])
        refresh_response = await client.post("/users/refresh")
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_refresh_token_missing(client):
    response = await client.post("/users/refresh")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Refresh token missing!"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    client.cookies.set("refresh_token", "invalidtoken")
    response = await client.post("/users/refresh")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials!"


@pytest.mark.asyncio
async def test_refresh_token_wrong_type(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        login_response = await client.post("/users/login", data={"username": test_user["contact_number"], "password": test_user["password"]})
        assert login_response.status_code == 200

        client.cookies.set("refresh_token", login_response.json()["access_token"])
        refresh_response = await client.post("/users/refresh")
        assert refresh_response.status_code == 401
        data = refresh_response.json()
        assert data["detail"] == "Could not validate credentials!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_refresh_token_unregistered_contact_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        fake_refresh_token = "invalid_refresh_token"
        client.cookies.set("refresh_token", fake_refresh_token)
        refresh_response = await client.post("/users/refresh")
        assert refresh_response.status_code == 401
        data = refresh_response.json()
        assert data["detail"] == "Could not validate credentials!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_refresh_token_expired(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        expired_refresh_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNjAwMDAwMDAwLCJ0eXBlIjoicmVmcmVzaCJ9.7n8sKqjLhXoWl8mN8v7u9n2e5tOa1kz5s9v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p"
        client.cookies.set("refresh_token", expired_refresh_token)
        refresh_response = await client.post("/users/refresh")
        assert refresh_response.status_code == 401
        data = refresh_response.json()
        assert data["detail"] == "Could not validate credentials!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_logout(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        login_response = await client.post("/users/login", data={"username": test_user["contact_number"], "password": test_user["password"]})
        assert login_response.status_code == 200

        client.cookies.set("access_token", login_response.json()["access_token"])
        client.cookies.set("refresh_token", login_response.json()["refresh_token"])
        logout_response = await client.post("/users/logout")
        assert logout_response.status_code == 200
        data = logout_response.json()
        assert data["Message"] == "Successfully Logged out!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_all_users(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        response = await client.get("/users/", headers={"Authorizataion": token})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_user_by_id(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        data = create_response.json()
        user_id = data["id"]
        response = await client.get(f"/users/{user_id}", headers={"Authorization": token})
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(client):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/users/{non_existent_user_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found!"


@pytest.mark.asyncio
async def test_get_user_by_contact_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        test_user = TEST_USER
        create_response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert create_response.status_code == 201
        response = await client.get(f"/users/contacts/{test_user["contact_number"]}")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_user_by_contact_number_not_found(client):
    response = await client.get("/users/contacts/0000000000")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found!"


@pytest.mark.asyncio
async def test_get_user_by_contact_number_invalid(client):
    response = await client.get("/users/contacts/invalid")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found!"


@pytest.mark.asyncio
async def test_get_current_user(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
            admin_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
            test_user = TEST_USER

            create_response = await client.post("/users/", json=test_user, headers={"Authorization": admin_token})
            assert create_response.status_code == 201

            login_response = await client.post(
                "/users/login",
                data={"username": test_user["contact_number"], "password": test_user["password"]},
            )
            assert login_response.status_code == 200

            access_token = login_response.json()["access_token"]
            response = await client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
            assert response.status_code == 200
            assert response.json()["contact_number"] == test_user["contact_number"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client):
    response = await client.get("/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    response = await client.get("users/me", headers={"Authorization": "invalid-token"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(client):
    expired_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNjc3ODQ4ODAwLCJ0eXBlIjoiYWNjZXNzIn0.7s8n"
    response = await client.get("/users/me", headers={"Authorization": expired_token})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials!"


@pytest.mark.asyncio
async def test_get_current_user_wrong_token_type(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        refresh_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoicmVmcmVzaCJ9.7s8n"
        response = await client.get("/users/me", headers={"Authorization": refresh_token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_current_user_unregistered_contact_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        fake_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwIiwiaWF0IjoxNjc3ODQ4ODAwLCJleHAiOjE3Nzg1MDU0NDcsInR5cCI6ImFjY2VzcyJ9.7s8n"
        response = await client.get("/users/me", headers={"Authorization": fake_token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"

        test_user = TEST_USER
        response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert response.status_code == 201
        data = response.json()
        assert data["contact_number"] == test_user["contact_number"]
        assert "id" in data
        assert "created_at" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_with_existing_contact_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"

        test_user = TEST_USER
        response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert response.status_code == 201

        # Try to create the same user again - should fail
        response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "User with this contact number already exists!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_unauthenticated(client):
    test_user = TEST_USER
    response = await client.post("/users/", json=test_user)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_user_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        test_user = TEST_USER
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can create new users!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_invalid_data(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["contact_number"] = "123"  # Invalid contact number

        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "contact_number"]
        assert data["detail"][0]["msg"] == "String should have at least 10 characters"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_invalid_role(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user =TEST_USER.copy()
        test_user["role"] = "invalid_role"  # Invalid role
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "role"]
        assert data["detail"][0]["msg"] == "Input should be 'chef', 'receptionist' or 'waiter'"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_short_password(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["password"] = "short"  # Password too short
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "password"]
        assert data["detail"][0]["msg"] == "String should have at least 8 characters"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_long_password(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["password"] = "p" * 129  # Password too long
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "password"]
        assert data["detail"][0]["msg"] == "String should have at most 128 characters"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_empty_first_name(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["first_name"] = ""  # Empty first name
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "first_name"]
        assert data["detail"][0]["msg"] == "String should have at least 1 character"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_empty_last_name(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["last_name"] = ""  # Empty last name
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "last_name"]
        assert data["detail"][0]["msg"] == "String should have at least 1 character"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_empty_contact_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["contact_number"] = ""  # Empty contact number
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "contact_number"]
        assert data["detail"][0]["msg"] == "String should have at least 10 characters"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_user_empty_password(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        test_user = TEST_USER.copy()
        test_user["password"] = ""  # Empty password
        response = await client.post("/users/", json=test_user)
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["loc"] == ["body", "password"]
        assert data["detail"][0]["msg"] == "String should have at least 8 characters"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_user(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"

        test_user = TEST_USER.copy()
        response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert response.status_code == 201
        data = response.json()
        user_id = data["id"]
        updated_user = {
            "first_name": "Updated",
        }
        updated_response = await client.patch(f"/users/{user_id}", json=updated_user, headers={"Authorization": token})
        assert updated_response.status_code == 200
        updated_data = updated_response.json()
        assert updated_data["first_name"] == "Updated"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_user_duplicate_contact_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"

        first_user = TEST_USER.copy()
        first_response = await client.post("/users/", json=first_user, headers={"Authorization": token})
        assert first_response.status_code == 201

        second_user = TEST_USER.copy()
        second_user["contact_number"] = "9876543211"
        second_response = await client.post("/users/", json=second_user, headers={"Authorization": token})
        assert second_response.status_code == 201

        first_user_id = first_response.json()["id"]
        duplicate_update = {
            "contact_number": second_user["contact_number"],
        }
        response = await client.patch(f"/users/{first_user_id}", json=duplicate_update, headers={"Authorization": token})
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "User with this contact number already exists!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_nonexistent_user(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        non_existent_user_id = "00000000-0000-0000-0000-000000000000"
        updated_user = {
            "first_name": "Updated"
        }
        response = await client.patch(f"/users/{non_existent_user_id}", json=updated_user, headers={"Authorization": token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_user_unauthenticated(client):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"
    updated_user = {
        "first_name": "Updated"
    }
    response = await client.patch(f"/users/{non_existent_user_id}", json=updated_user)
    assert response.status_code ==401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_user_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwOTg3NjU0MzIxMCIsImV4cCI6MTc3ODUwNTQ0NywidHlwZSI6ImFjY2VzcyJ9.7n8sKqjLhXoWl8mN8v7u9n2e5tOa1kz5s9v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p"
        user_id = "00000000-0000-0000-0000-000000000000" # This can be any valid UUID since the test is checking for forbidden access, not user existence
        updated_user = {
            "first_name": "Updated"
        }
        updated_response = await client.patch(f"/users/{user_id}", json=updated_user, headers={"Authorization": token})
        assert updated_response.status_code == 403
        updated_data = updated_response.json()
        assert updated_data["detail"] == "You can only update your own profile!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_user(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"

        test_user = TEST_USER.copy()
        response = await client.post("/users/", json=test_user, headers={"Authorization": token})
        assert response.status_code == 201
        data = response.json()
        user_id = data["id"]
        delete_response = await client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["message"] == f"{test_user['first_name']} {test_user['last_name']} has been deleted successfully!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        non_existent_user_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/users/{non_existent_user_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_user_unauthenticated(client):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/users/{non_existent_user_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_user_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwOTg3NjU0MzIxMCIsImV4cCI6MTc3ODUwNTQ0NywidHlwZSI6ImFjY2VzcyJ9.7n8sKqjLhXoWl8mN8v7u9n2e5tOa1kz5s9v1w2x3y4z5a6b7c8d9e0f1g2h3i4j5k6l7m8n9o0p"
        user_id = "00000000-0000-0000-0000-000000000000" # This can be any valid UUID since the test is checking for forbidden access, not user existence
        response = await client.delete(f"/users/{user_id}", headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "You can only delete your own profile!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
