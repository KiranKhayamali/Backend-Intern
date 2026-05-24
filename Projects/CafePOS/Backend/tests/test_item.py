import pytest

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from .test_user import _fake_admin_user, _fake_non_admin_user


TEST_ITEM = {
    "order_id": "00000000-0000-0000-0000-000000000000",
    "dish_id": "00000000-0000-0000-0000-000000000000",
    "quantity": 2,
    "quantity_type": "plate",
    "remark": "Test item remark",
    "status": "pending"
}


async def _create_valid_item_dependencies(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDE5ZGY3MDYtN2NmMy03YTQ1LWFjMWMtNzVkYWFhZDAtZjU0ZCIsImV4cCI6MTcwMTg4ODQwMH0.7n8sHqjKkKz8l9mLh7e3u9"

        table_response = await client.post(
            "/tables/",
            json={"number": 1, "capacity": 4, "status": "available"},
            headers={"Authorization": token}
        )
        assert table_response.status_code == 201
        table_id = table_response.json()["id"]

        user_response = await client.post(
            "/users/",
            json={
                "first_name": "Order",
                "middle_name": None,
                "last_name": "User",
                "contact_number": "9999999999",
                "is_admin": False,
                "role": "waiter",
                "password": "password123",
            },
            headers={"Authorization": token}
        )
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]

        order_response = await client.post("/orders/", json={
            "table_id": table_id,
            "user_id": user_id,
            "status": "idle",
            "remark": "Test order for item"
        }, headers={"Authorization": token})
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]

        dish_response = await client.post(
            "/dishes/",
            json={
                "name": "Test Dish",
                "description": "A dish for testing",
                "price": 1000,
                "category": "Main Course",
                "dish_type": "Vegetarian"
            },
            headers={"Authorization": token}
        )
        assert dish_response.status_code == 201
        dish_id = dish_response.json()["id"]

        return order_id, dish_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_create_item(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    test_item = TEST_ITEM.copy()
    test_item["order_id"] = order_id
    test_item["dish_id"] = dish_id
    response = await client.post("/items/", json=test_item)
    assert response.status_code == 201
    data = response.json()
    assert data["remark"] == test_item["remark"]
    assert data["quantity"] == test_item["quantity"]
    assert data["quantity_type"] == test_item["quantity_type"]
    assert data["status"] == test_item["status"]


@pytest.mark.asyncio
async def test_create_item_invalid_order(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    invalid_item = TEST_ITEM.copy()
    invalid_item["order_id"] = "00000000-0000-0000-0000-000000000000"
    invalid_item["dish_id"] = dish_id
    response = await client.post("/items/", json=invalid_item)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Order not Found!"


@pytest.mark.asyncio
async def test_create_item_invalid_dish(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    invalid_item = TEST_ITEM.copy()
    invalid_item["order_id"] = order_id
    invalid_item["dish_id"] = "00000000-0000-0000-0000-000000000000"
    response = await client.post("/items/", json=invalid_item)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Dish not Found!"


@pytest.mark.asyncio
async def test_create_item_missing_fields(client):
    response = await client.post("/items/", json={})
    assert response.status_code == 422
    data = response.json()
    assert "order_id" in str(data)
    assert "dish_id" in str(data)


@pytest.mark.asyncio
async def test_create_item_invalid_quantity(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    invalid_item = TEST_ITEM.copy()
    invalid_item["order_id"] = order_id
    invalid_item["dish_id"] = dish_id
    invalid_item["quantity"] = -1
    response = await client.post("/items/", json=invalid_item)
    assert response.status_code == 422
    data = response.json()
    assert "quantity" in str(data)


@pytest.mark.asyncio
async def test_create_item_invalid_status(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    invalid_item = TEST_ITEM.copy()
    invalid_item["order_id"] = order_id
    invalid_item["dish_id"] = dish_id
    invalid_item["status"] = "invalid_status"
    response = await client.post("/items/", json=invalid_item)
    assert response.status_code == 422
    data = response.json()
    assert "status" in str(data)


@pytest.mark.asyncio
async def test_get_all_items(client):
    response = await client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_item_by_id(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    test_item = TEST_ITEM.copy()
    test_item["order_id"] = order_id
    test_item["dish_id"] = dish_id
    create_response = await client.post("/items/", json=test_item)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id


@pytest.mark.asyncio
async def test_get_item_by_id_not_found(client):
    item_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not Found!"


@pytest.mark.asyncio
async def test_update_item(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    test_item = TEST_ITEM.copy()
    test_item["order_id"] = order_id
    test_item["dish_id"] = dish_id
    create_response = await client.post("/items/", json=test_item)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    updated_item = {
        "quantity": 3,
        "quantity_type": "bowl",
        "remark": "Updated item remark",
        "status": "in_progress"
    }
    response = await client.patch(f"/items/{item_id}", json=updated_item)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == updated_item["quantity"]
    assert data["quantity_type"] == updated_item["quantity_type"]
    assert data["remark"] == updated_item["remark"]
    assert data["status"] == updated_item["status"]


@pytest.mark.asyncio
async def test_update_item_not_found(client):
    item_id = "00000000-0000-0000-0000-000000000000"
    updated_item = {
        "quantity": 3,
        "quantity_type": "bowl",
        "remark": "Updated item remark",
        "status": "in_progress"
    }
    response = await client.patch(f"/items/{item_id}", json=updated_item)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not Found!"


@pytest.mark.asyncio
async def test_update_item_invalid_status(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    test_item = TEST_ITEM.copy()
    test_item["order_id"] = order_id
    test_item["dish_id"] = dish_id
    create_response = await client.post("/items/", json=test_item)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    updated_item = {
        "quantity": 3,
        "quantity_type": "bowl",
        "remark": "Updated item remark",
        "status": "Invalid Status"
    }
    response = await client.patch(f"/items/{item_id}", json=updated_item)
    assert response.status_code == 422
    data = response.json()
    assert "status" in str(data)


@pytest.mark.asyncio
async def test_update_item_invalid_quantity(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    test_item = TEST_ITEM.copy()
    test_item["order_id"] = order_id
    test_item["dish_id"] = dish_id
    create_response = await client.post("/items/", json=test_item)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    updated_item = {
        "quantity": -2,
        "quantity_type": "bowl",
        "remark": "Updated item remark",
        "status": "in_progress"
    }
    response = await client.patch(f"/items/{item_id}", json=updated_item)
    assert response.status_code == 422
    data = response.json()
    assert "quantity" in str(data)


@pytest.mark.asyncio
async def test_delete_item(client):
    order_id, dish_id = await _create_valid_item_dependencies(client)
    test_item = TEST_ITEM.copy()
    test_item["order_id"] = order_id
    test_item["dish_id"] = dish_id
    create_response = await client.post("/items/", json=test_item)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    response = await client.delete(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["Message"] == f"Item with id {item_id} has been deleted successfully!"


@pytest.mark.asyncio
async def test_delete_item_not_found(client):
    item_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/items/{item_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item not Found!"
