import pytest

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from Projects.CafePOS.Backend.src.app.models.sections import Section
from .test_user import _fake_admin_user, _fake_non_admin_user

TEST_SECTION = {
    "name": "Test Section"
}


@pytest.mark.asyncio
async def test_create_section(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        response = await client.post("/sections/", json=TEST_SECTION, headers={"Authorization": token})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == TEST_SECTION["name"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_section_unauthorized(client):
    response = await client.post("/sections/", json=TEST_SECTION)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_section_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc"
        response = await client.post("/sections/", json=TEST_SECTION, headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can create new sections!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_all_sections(client):
    response = await client.get("/sections/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_section_by_id(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/sections/", json=TEST_SECTION, headers={"Authorization": token})
        assert create_response.status_code == 201
        section_id = create_response.json()["id"]
        response = await client.get(f"/sections/{section_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == section_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_section_by_id_not_found(client):
    section_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/sections/{section_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Section not Found!"


@pytest.mark.asyncio
async def test_get_section_by_name(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/sections/", json=TEST_SECTION, headers={"Authorization": token})
        assert create_response.status_code == 201
        section_name = create_response.json()["name"]
        response = await client.get(f"/sections/names/{section_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == section_name
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_section_by_name_not_found(client):
    section_name = "NonExistentSection"
    response = await client.get(f"/sections/names/{section_name}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Section not Found!"


@pytest.mark.asyncio
async def test_update_section(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/sections/", json=TEST_SECTION, headers={"Authorization": token})
        assert create_response.status_code == 201
        section_id = create_response.json()["id"]
        updated_data = {"name": "Updated Section Name"}
        response = await client.patch(f"/sections/{section_id}", json=updated_data, headers={"Authorization": token})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == section_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_section_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        section_id = "00000000-0000-0000-0000-000000000000"
        updated_data = {"name": "Updated Section Name"}
        response = await client.patch(f"/sections/{section_id}", json=updated_data, headers={"Authorization": token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Section not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_section_unauthenticated(client):
    section_id = "019e0098-5122-7f11-a93a-78660594e676"
    updated_data = {"name": "Updated Rooftop Section"}
    response = await client.patch(f"/sections/{section_id}", json=updated_data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_section_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        section_id = "019e0098-5122-7f11-a93a-78660594e676"
        updated_data = {"name": "Updated Rooftop Section"}
        response = await client.patch(f"/sections/{section_id}", json=updated_data, headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can update sections!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_section(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        create_response = await client.post("/sections/", json=TEST_SECTION, headers={"Authorization": token})
        assert create_response.status_code == 201
        section_id = create_response.json()["id"]
        section_name = create_response.json()["name"]
        response = await client.delete(f"/sections/{section_id}", headers={"Authorization": token})
        assert response.status_code == 200
        data = response.json()
        assert data["Message"] == f"{section_name} has been successfully deleted!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_section_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        section_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/sections/{section_id}", headers={"Authorization": token})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Section not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_section_unauthenticated(client):
    section_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/sections/{section_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_section_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwiZXhwIjoxNzc4NTA1NDQ3LCJ0eXBlIjoiYWNjZXNzIn0.QA1frn1pjOLObe2j5vmJIzzwRIRhUfD3UTNSuz7y6ME"
        section_id = "019e0098-5122-7f11-a93a-78660594e676"
        response = await client.delete(f"/sections/{section_id}", headers={"Authorization": token})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can delete sections!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


