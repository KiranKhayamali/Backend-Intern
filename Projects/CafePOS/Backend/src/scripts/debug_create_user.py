import asyncio

import httpx

from Projects.CafePOS.Backend.src.main import app
from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user


async def _fake_admin_user():
    from Projects.CafePOS.Backend.src.app.models.users import User

    return User(
        first_name="Admin",
        middle_name="",
        last_name="User",
        contact_number="1234567890",
        is_admin=True,
        role="waiter",
        hashed_password="password123",
    )


async def main():
    app.dependency_overrides[get_current_user] = _fake_admin_user

    test_user = {
        "first_name": "Test",
        "middle_name": "",
        "last_name": "User",
        "contact_number": "1122334455",
        "is_admin": False,
        "role": "waiter",
        "password": "password123",
    }

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/users/", json=test_user, headers={"Authorization": "Bearer dummy"})
        print("status:", response.status_code)
        try:
            print("json:", response.json())
        except Exception:
            print("text:", response.text)


if __name__ == "__main__":
    asyncio.run(main())
