from database import sessionLocal

async def get_db():
    db = sessionLocal()
    try:
        yield db 
    finally:
        await db.close()