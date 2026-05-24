import pytest
from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from .test_user import _fake_admin_user, _fake_non_admin_user

TEST_BILL = {
    "customer_name": "Test Customer",
    "customer_contact": "1234567890",
    "payment_method": "cash",
    "order_id": "019e00fa-3a88-7dfd-a499-ac83c008094f",
    "table_id": "019e00fa-3a88-7dfd-a499-ac83c008094f",
    "user_id": "019df706-7cf3-7a45-ac1c-75daaad0f54d"
}

async def _create_valid_bill_dependencies(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        table_response = await client.post(
            "/tables/",
            json={
                "number": 101,
                "capacity": 4,
                "status": "available"
            }
        )
        assert table_response.status_code == 201, f"Table creation failed: {table_response.text}"
        table_id = table_response.json()["id"]

        user_response = await client.post(
            "/users/",
            json={
                "first_name": "Test",
                "middle_name": None,
                "last_name": "User",
                "contact_number": "9999999999",
                "is_admin": False,
                "role": "receptionist",
                "password": "password123"
            }
        )
        assert user_response.status_code == 201, f"User creation failed: {user_response.text}"
        user_id = user_response.json()["id"]

        order_response = await client.post(
            "/orders/",
            json={
                "table_id": table_id,
                "user_id": user_id,
                "status": "open",
                "remark": "Test order for bill dependencies"
            }
        )
        assert order_response.status_code == 201, f"Order creation failed: {order_response.text}"
        order_id = order_response.json()["id"]

        dish_response = await client.post(
            "/dishes/",
            json={
                "name": "Test Dish for Bill",
                "description": "A dish for bill testing",
                "price": 500,
                "category": "Main Course",
                "dish_type": "Vegetarian"
            }
        )
        assert dish_response.status_code == 201, f"Dish creation failed: {dish_response.text}"
        dish_id = dish_response.json()["id"]

        item_response = await client.post(
            "/items/",
            json={
                "order_id": order_id,
                "dish_id": dish_id,
                "quantity": 2,
                "quantity_type": "plate",
                "remark": "Test item for bill",
                "status": "pending"
            }
        )
        assert item_response.status_code == 201, f"Item creation failed: {item_response.text}"

        return order_id, table_id, user_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)

async def _create_response(client, url: str = "/bills/", json_data: dict = TEST_BILL):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        response = await client.post(url, json=json_data)
        return response
    finally:
        app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_create_bill(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    response = await _create_response(client, json_data=test_bill)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == test_bill["customer_name"]
    assert data["customer_contact"] == test_bill["customer_contact"]
    assert data["payment_method"] == test_bill["payment_method"]

@pytest.mark.asyncio
async def test_create_bill_invalid_order(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    invalid_bill = TEST_BILL.copy()
    invalid_bill["order_id"] = "00000000-0000-0000-0000-000000000000"
    invalid_bill["table_id"] = table_id
    invalid_bill["user_id"] = user_id
    response = await _create_response(client, json_data=invalid_bill)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == f"Order with id {invalid_bill['order_id']} not found"

@pytest.mark.asyncio
async def test_create_bill_empty_order(client):
    # Set override for creating dependencies
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
        empty_order_response = await client.post(
            "/orders/",
            json={
                "table_id": table_id,
                "user_id": user_id,
                "status": "open",
                "remark": "Test empty order for bill dependencies"
            }
        )
        assert empty_order_response.status_code == 201
        empty_order_id = empty_order_response.json()["id"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    invalid_bill = TEST_BILL.copy()
    invalid_bill["order_id"] = empty_order_id
    invalid_bill["table_id"] = table_id
    invalid_bill["user_id"] = user_id
    response = await _create_response(client, json_data=invalid_bill)
    assert response.status_code == 400
    data = response.json()
    assert "order has no items" in data["detail"]

@pytest.mark.asyncio
async def test_create_bill_invalid_table(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    invalid_bill = TEST_BILL.copy()
    invalid_bill["order_id"] = order_id
    invalid_bill["table_id"] = "00000000-0000-0000-0000-000000000000"
    invalid_bill["user_id"] = user_id
    response = await _create_response(client, json_data=invalid_bill)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Table not Found!"

@pytest.mark.asyncio
async def test_create_bill_invalid_user(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    invalid_bill = TEST_BILL.copy()
    invalid_bill["order_id"] = order_id
    invalid_bill["table_id"] = table_id
    invalid_bill["user_id"] = "00000000-0000-0000-0000-000000000000"
    response = await _create_response(client, json_data=invalid_bill)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not Found!"

@pytest.mark.asyncio
async def test_create_bill_missing_fields(client):
    response = await _create_response(client, json_data={})
    assert response.status_code == 422
    data = response.json()
    assert "order_id" in str(data)
    assert "table_id" in str(data)
    assert "user_id" in str(data)

@pytest.mark.asyncio
async def test_create_bill_invalid_payment_method(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    invalid_bill = TEST_BILL.copy()
    invalid_bill["order_id"] = order_id
    invalid_bill["table_id"] = table_id
    invalid_bill["user_id"] = user_id
    invalid_bill["payment_method"] = "invalid_method"
    response = await _create_response(client, json_data=invalid_bill)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_bill_unauthenticated(client):
    response = await client.post("/bills/", json=TEST_BILL)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_bill_forbidden(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)

    # Create a waiter user (non-admin, non-receptionist)
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        waiter_response = await client.post(
            "/users/",
            json={
                "first_name": "Test",
                "middle_name": None,
                "last_name": "Waiter",
                "contact_number": "7777777777",
                "is_admin": False,
                "role": "waiter",
                "password": "password123"
            }
        )
        assert waiter_response.status_code == 201
        waiter_id = waiter_response.json()["id"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    # Now attempt to create a bill with the waiter user
    forbidden_bill = TEST_BILL.copy()
    forbidden_bill["order_id"] = order_id
    forbidden_bill["table_id"] = table_id
    forbidden_bill["user_id"] = waiter_id

    response = await _create_response(client, json_data=forbidden_bill)
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Only receptionists and admins can create bills!"


@pytest.mark.asyncio
async def test_get_all_bills(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        response = await client.get("/bills/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_all_bills_unauthenticated(client):
    response = await client.get("/bills/")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_all_bills_forbidden(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201

    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        response = await client.get("/bills/")
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only receptionists and admins can access bills!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_bill_by_id(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        response = await client.get(f"/bills/{bill_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == bill_id
        assert data["customer_name"] == test_bill["customer_name"]
        assert data["customer_contact"] == test_bill["customer_contact"]
        assert data["payment_method"] == test_bill["payment_method"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_bill_by_id_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        bill_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/bills/{bill_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == f"Bill with ID {bill_id} not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_get_bill_by_id_unauthenticated(client):
    bill_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/bills/{bill_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_bill_by_id_forbidden(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        response = await client.get(f"/bills/{bill_id}")
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only receptionists and admins can access bill details!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    updated_data = {
        "customer_name": "Updated Customer",
        "payment_method": "card"
    }
    try:
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == bill_id
        assert data["customer_name"] == updated_data["customer_name"]
        assert data["payment_method"] == updated_data["payment_method"]
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        bill_id = "00000000-0000-0000-0000-000000000000"
        updated_data = {
            "customer_name": "Updated Customer",
            "payment_method": "card"
        }
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Bill not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill_unauthenticated(client):
    bill_id = "00000000-0000-0000-0000-000000000000"
    updated_data = {
        "customer_name": "Updated Customer",
        "payment_method": "card"
    }
    response = await client.patch(f"/bills/{bill_id}", json=updated_data)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_bill_forbidden(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    updated_data = {
        "customer_name": "Updated Customer",
        "payment_method": "card"
    }
    try:
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only receptionists and admins can update bills!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill_invalid_payment_method(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    updated_data = {
        "payment_method": "invalid_method"
    }
    try:
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 422
        data = response.json()
        assert "payment_method" in str(data)
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill_invalid_order_id(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    updated_data = {
        "order_id": "00000000-0000-0000-0000-000000000000"
    }
    try:
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == f"Order with id {updated_data['order_id']} not found"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill_invalid_table_id(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    updated_data = {
        "table_id": "00000000-0000-0000-0000-000000000000"
    }
    try:
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Table not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_update_bill_invalid_user_id(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    updated_data = {
        "user_id": "00000000-0000-0000-0000-000000000000"
    }
    try:
        response = await client.patch(f"/bills/{bill_id}", json=updated_data)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_bill(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        response = await client.delete(f"/bills/{bill_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["Message"] == f"Bill with id {bill_id} has been deleted successfully!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_bill_not_found(client):
    app.dependency_overrides[get_current_user] = _fake_admin_user
    try:
        bill_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/bills/{bill_id}")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Bill not Found!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_delete_bill_unauthenticated(client):
    bill_id = "00000000-0000-0000-0000-000000000000"
    response = await client.delete(f"/bills/{bill_id}")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_delete_bill_forbidden(client):
    order_id, table_id, user_id = await _create_valid_bill_dependencies(client)
    test_bill = TEST_BILL.copy()
    test_bill["order_id"] = order_id
    test_bill["table_id"] = table_id
    test_bill["user_id"] = user_id
    create_response = await _create_response(client, json_data=test_bill)
    assert create_response.status_code == 201
    bill_id = create_response.json()["id"]

    app.dependency_overrides[get_current_user] = _fake_non_admin_user
    try:
        response = await client.delete(f"/bills/{bill_id}")
        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Only receptionists and admins can delete bills!"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
