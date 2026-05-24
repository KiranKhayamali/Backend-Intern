import pytest

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user

from .test_user import _fake_admin_user


TEST_ORDER = {
    "table_id": "019e00fa-3a88-7dfd-a499-ac83c008094f",
    "user_id": "019df706-7cf3-7a45-ac1c-75daaad0f54d",
    "status": "idle",
    "remark": "Test order remark"
}


async def _create_valid_order_dependencies(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        table_response = await client.post("/tables/", json={"number": 101, "capacity": 4, "status": "available"})
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
        )
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]
        return table_id, user_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)



@pytest.mark.asyncio
async def test_create_order(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    order_payload = TEST_ORDER.copy()
    order_payload["table_id"] = table_id
    order_payload["user_id"] = user_id
    response = await client.post("/orders/", json=order_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["remark"] == order_payload["remark"]
    assert data["status"] == order_payload["status"]


@pytest.mark.asyncio
async def test_create_order_invalid_table(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    invalid_order = TEST_ORDER.copy()
    invalid_order["table_id"] = "00000000-0000-0000-0000-000000000000"
    invalid_order["user_id"] = user_id
    response = await client.post("/orders/", json=invalid_order)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Table not Found!"


@pytest.mark.asyncio
async def test_create_order_invalid_user(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    invalid_order = TEST_ORDER.copy()
    invalid_order["table_id"] = table_id
    invalid_order["user_id"] = "00000000-0000-0000-0000-000000000000"
    response = await client.post("/orders/", json=invalid_order)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found!"


@pytest.mark.asyncio
async def test_create_order_missing_fields(client):
    response = await client.post("/orders/", json={})
    assert response.status_code == 422
    data = response.json()
    assert "table_id" in str(data)
    assert "user_id" in str(data)


@pytest.mark.asyncio
async def test_create_order_invalid_status(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    invalid_order = TEST_ORDER.copy()
    invalid_order["table_id"] = table_id
    invalid_order["user_id"] = user_id
    invalid_order["status"] = "invalid_status"
    response = await client.post("/orders/", json=invalid_order)
    assert response.status_code == 422
    data = response.json()
    assert "status" in str(data)


@pytest.mark.asyncio
async def test_get_all_orders(client):
    response = await client.get("/orders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_order_by_id(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    test_order = TEST_ORDER.copy()
    test_order["table_id"] = table_id
    test_order["user_id"] = user_id
    create_response = await client.post("/orders/", json=test_order)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]
    response = await client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id


@pytest.mark.asyncio
async def test_get_order_by_id_not_found(client):
    order_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/orders/{order_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Order not Found!"


@pytest.mark.asyncio
async def test_get_order_by_id_invalid_uuid(client):
    response = await client.get("/orders/invalid-uuid")
    assert response.status_code == 422
    data = response.json()
    assert "Input should be a valid UUID" in str(data)


@pytest.mark.asyncio
async def test_update_order(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    test_order = TEST_ORDER.copy()
    test_order["table_id"] = table_id
    test_order["user_id"] = user_id
    create_response = await client.post("/orders/", json=test_order)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]
    updated_payload = {"status": "in_progress", "remark": "Updated remark"}
    response = await client.patch(f"/orders/{order_id}", json=updated_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == updated_payload["status"]
    assert data["remark"] == updated_payload["remark"]


@pytest.mark.asyncio
async def test_update_order_not_found(client):
    order_id = "00000000-0000-0000-0000-000000000000"
    updated_payload = {"status": "in_progress", "remark": "Updated remark"}
    response = await client.patch(f"/orders/{order_id}", json=updated_payload)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Order not Found!"


@pytest.mark.asyncio
async def test_update_order_invalid_status(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    test_order = TEST_ORDER.copy()
    test_order["table_id"] = table_id
    test_order["user_id"] = user_id
    create_response = await client.post("/orders/", json=test_order)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]
    updated_payload = {"status": "invalid_status", "remark": "Updated remark"}
    response = await client.patch(f"/orders/{order_id}", json=updated_payload)
    assert response.status_code == 422
    data = response.json()
    assert "status" in str(data)


@pytest.mark.asyncio
async def test_delete_order(client):
    table_id, user_id = await _create_valid_order_dependencies(client)
    test_order = TEST_ORDER.copy()
    test_order["table_id"] = table_id
    test_order["user_id"] = user_id
    create_response = await client.post("/orders/", json=test_order)
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]
    response = await client.delete(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["Message"] == "Order has been deleted successfully!"


@pytest.mark.asyncio
async def test_delete_order_not_found(client):
    order_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/orders/{order_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Order not Found!"


@pytest.mark.asyncio
async def test_delete_order_invalid_uuid(client):
    response = await client.delete("/orders/invalid-uuid")
    assert response.status_code == 422
    data = response.json()
    assert "Input should be a valid UUID" in str(data)

