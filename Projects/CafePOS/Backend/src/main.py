from fastapi import FastAPI
from contextlib import asynccontextmanager

from .app.core.schemas import HealthCheck
from .app.core.db.database import init_db
from .app.api.user_route import user_router
from .app.api.dish_route import dish_router
from .app.api.section_route import section_router
from .app.api.table_route import table_router
from .app.api.order_route import order_router
from .app.api.item_route import item_router
from .app.api.bill_route import bill_router
from .app.core.utils.first_admin import initialize_first_admin_user
from .app.repositories.user_repository import UserRepository
from .app.core.db.session import async_session

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application.....")
    await init_db()

    async with async_session() as db:
        user_repo = UserRepository(db=db)
        await initialize_first_admin_user(user_repo)

    yield

    print("Shutting down the application.....")


app = FastAPI(lifespan=lifespan, title="CafePOS Backend API", version="1.0.0", description="API for managing cafe operations, including users, orders, and inventory.")




@app.get("/")
def read_root():
    return {"message": "Welcome to CafePOS Backend API!"}

@app.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(status="healthy")


# Include API routers
app.include_router(user_router)
app.include_router(dish_router)
app.include_router(section_router)
app.include_router(table_router)
app.include_router(order_router)
app.include_router(item_router)
app.include_router(bill_router)



# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)