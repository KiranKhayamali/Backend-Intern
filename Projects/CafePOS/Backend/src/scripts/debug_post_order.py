import asyncio
import json
from httpx import AsyncClient
from Projects.CafePOS.Backend.src.main import app

TEST_ORDER = {
    "table_id": "019e00fa-3a88-7dfd-a499-ac83c008094f",
    "user_id": "019df706-7cf3-7a45-ac1c-75daaad0f54d",
    "status": "idle",
    "remark": "Test order remark"
}

async def main():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/orders/", json=TEST_ORDER)
        print('STATUS:', r.status_code)
        try:
            print('JSON:', json.dumps(r.json(), indent=2))
        except Exception:
            print('TEXT:', r.text)

if __name__ == '__main__':
    asyncio.run(main())
