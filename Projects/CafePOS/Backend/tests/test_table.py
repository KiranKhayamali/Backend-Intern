import pytest

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from Projects.CafePOS.Backend.src.app.models.tables import Table
from .test_user import _fake_admin_user, _fake_non_admin_user


TEST_TABLE = {
    "number": 1,
    "capacity": 4
}


@pytest.mark.asyncio
async def test_create_table(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        response = await client.post("/tables/", json=TEST_TABLE, headers={"Authorization": token})
        assert response.status_code == 201
        data = response.json()
        assert data["number"] == TEST_TABLE["number"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_table_unauthorized(client):
    response = await client.post("/tables/", json=TEST_TABLE)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_table_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        response = await client.post("/tables/", json=TEST_TABLE, headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can create new tables!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_all_tables(client):
    response = await client.get("/tables/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_table_by_id(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/tables/", json=TEST_TABLE, headers={"Authorization": token})
        assert create_response.status_code == 201
        table_id = create_response.json()["id"]

        response = await client.get(f"/tables/{table_id}")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == table_id


@pytest.mark.asyncio
async def test_get_table_by_id_not_found(client):
    table_id = "12345678-1234-1234-1234-123456789012"
    response = await client.get(f"/tables/{table_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Table not Found!"


@pytest.mark.asyncio
async def test_get_table_by_number(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/tables/", json=TEST_TABLE, headers={"Authorization": token})
        assert create_response.status_code == 201
        table_number = create_response.json()["number"]
        response = await client.get(f"/tables/numbers/{table_number}")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == table_number
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_table_by_number_not_found(client):
    table_number = 999
    response = await client.get(f"/tables/numbers/{table_number}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Table number {table_number} not Found!"


@pytest.mark.asyncio
async def test_get_table_by_number_bad_request(client):
    table_number = "invalid"
    response = await client.get(f"/tables/numbers/{table_number}")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_table(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/tables/", json=TEST_TABLE, headers={"Authorization": token})
        assert create_response.status_code == 201
        table_id = create_response.json()["id"]
        response = await client.patch(f"/tables/{table_id}", json={"capacity": 6}, headers={"Authorization": token})
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 6
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_table_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        table_id = "12345678-1234-1234-1234-123456789012"
        response = await client.patch(f"/tables/{table_id}", json={"capacity": 6}, headers={"Authorization": token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Table not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_table_unauthenticated(client):
    table_id = "12345678-1234-1234-1234-123456789012"
    response = await client.patch(f"/tables/{table_id}", json={"capacity": 6})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_table_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        table_id = "12345678-1234-1234-1234-123456789012"
        response = await client.patch(f"/tables/{table_id}", json={"capacity": 6}, headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can update tables!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_table(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/tables/", json=TEST_TABLE, headers={"Authorization": token})
        assert create_response.status_code == 201
        table_id = create_response.json()["id"]
        table_number = create_response.json()["number"]
        response = await client.delete(f"/tables/{table_id}", headers={"Authorization": token})
        assert response.status_code == 200
        data = response.json()
        assert data["Message"] == f"Table {table_number} has been successfully deleted!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_table_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        table_id = "12345678-1234-1234-1234-123456789012"
        response = await client.delete(f"/tables/{table_id}", headers={"Authorization": token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Table not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_table_unauthenticated(client):
    table_id = "12345678-1234-1234-1234-123456789012"
    response = await client.delete(f"/tables/{table_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_table_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        table_id = "12345678-1234-1234-1234-123456789012"
        response = await client.delete(f"/tables/{table_id}", headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can delete tables!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
