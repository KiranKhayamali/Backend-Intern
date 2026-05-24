import pytest

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from .test_user import _fake_admin_user, _fake_non_admin_user


TEST_DISH = {
    "name": "Test Dish",
    "description": "A delicious test dish",
    "price": 1000,
    "category": "Main Course",
    "dish_type": "Veg"
}


@pytest.mark.asyncio
async def test_create_dish(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        response = await client.post("/dishes/", json=TEST_DISH)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == TEST_DISH["name"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_dish_unauthenticated(client):
    response = await client.post("/dishes/", json=TEST_DISH)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_dish_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        response = await client.post("/dishes/", json=TEST_DISH)
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admins can create dishes!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_dish_invalid_data(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        invalid_dish = TEST_DISH.copy()
        invalid_dish["price"] = -100
        response = await client.post("/dishes/", json=invalid_dish)
        assert response.status_code == 422
        data = response.json()
        assert "price" in str(data["detail"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_dish_extra_fields(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        dish_with_extra_fields = TEST_DISH.copy()
        dish_with_extra_fields["extra_field"] = "Extra dish field"
        response = await client.post("/dishes/", json=dish_with_extra_fields)
        assert response.status_code == 422
        data = response.json()
        assert "extra_field" in str(data["detail"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_dish_missing_fields(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        incomplete_dish = {
            "name": "Incomplete Dish",
            "price": 599
        }
        response = await client.post("/dishes/", json=incomplete_dish)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == incomplete_dish["name"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_all_dishes(client):
    response = await client.get("/dishes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_dish_by_id(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        create_response = await client.post("/dishes/", json=TEST_DISH)
        assert create_response.status_code == 201
        created_dish = create_response.json()
        dish_id = created_dish["id"]
        response = await client.get(f"/dishes/{dish_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == dish_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_dish_by_id_not_found(client):
    dish_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/dishes/{dish_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Dish not Found!"


@pytest.mark.asyncio
async def test_get_dish_by_id_invalid_uuid(client):
    invalid_dish_id = "invalid-uuid0"
    response = await client.get(f"/dishes/{invalid_dish_id}")
    assert response.status_code == 422
    data = response.json()
    assert "Input should be a valid UUID" in str(data)


@pytest.mark.asyncio
async def test_get_dish_by_name(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        create_response = await client.post("/dishes/", json=TEST_DISH)
        assert create_response.status_code == 201
        created_dish = create_response.json()
        dish_name = created_dish["name"]
        response = await client.get(f"/dishes/names/{dish_name}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["name"] == dish_name
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_dish_by_name_not_found(client):
    dish_name = "Non Existent Dish"
    response = await client.get(f"/dishes/names/{dish_name}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Dish not Found!"


@pytest.mark.asyncio
async def test_update_dish(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        create_response = await client.post("/dishes/", json=TEST_DISH)
        assert create_response.status_code == 201
        created_dish = create_response.json()
        dish_id = created_dish["id"]
        updated_data = {
            "price": 699,
        }

        response = await client.patch(f"/dishes/{dish_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == dish_id
        assert data["price"] == updated_data["price"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_dish_unauthenticated(client):
    dish_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(f"/dishes/{dish_id}", json={"price": 699})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_dish_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        dish_id = "019e0034-d235-76be-87a2-3afbd8d15087"
        response = await client.patch(f"/dishes/{dish_id}", json={"price": 299})
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can update dishes!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_dish_invalid_data(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        create_response = await client.post("/dishes/", json=TEST_DISH)
        assert create_response.status_code == 201
        created_dish = create_response.json()
        dish_id = created_dish["id"]
        invalid_update = {
            "price": -200
        }

        response = await client.patch(f"/dishes/{dish_id}", json=invalid_update)
        assert response.status_code == 422
        data = response.json()
        assert "price" in str(data["detail"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_dish_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        dish_id = "00000000-0000-0000-0000-000000000000"
        response = await client.patch(f"/dishes/{dish_id}", json={"price": 299})
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Dish not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_dish(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        create_response = await client.post("/dishes/", json=TEST_DISH)
        assert create_response.status_code == 201
        created_dish = create_response.json()
        dish_id = created_dish["id"]
        dish_name = created_dish["name"]

        response = await client.delete(f"/dishes/{dish_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["Message"] == f"{dish_name} has been successfully deleted!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_dish_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        dish_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/dishes/{dish_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Dish not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_dish_unauthenticated(client):
    dish_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/dishes/{dish_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_dish_forbidden(client):
    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        dish_id = "019e0034-d235-76be-87a2-3afbd8d15087"
        response = await client.delete(f"/dishes/{dish_id}")
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only admin users can delete dishes!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
