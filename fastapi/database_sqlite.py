from typing import Annotated
from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager

#Creating a model
# class Hero(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     hero_name: str = Field(index=True) #index can be used to search for while using query
#     full_name: str #The hero's real name is publicly showcased

#Creating Multiple Models
class HeroBase(SQLModel):
    hero_name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str

class HeroPublic(HeroBase):
    id: int

class HeroCreate(HeroBase):
    full_name: str

class HeroUpdate(HeroBase):
    hero_name: str| None = None 
    age: int | None = None 
    full_name: str | None = None


#Creating a engine
sqlite_file_name = "sqlite_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connected_args = {"check_same_thread": False} # it also FastAPI to use same DB in different thread, as one request could use more than one thread(eg: dependencies)
engine = create_engine(sqlite_url, connect_args=connected_args) #engine holds the connection to the database

#Creating the table 
def create_db_and_tables_in_sqlite():
    SQLModel.metadata.create_all(engine)

#Creating Session Dependency 
def get_session():
    with Session(engine) as session: #session stores the objects in memory and keeps tracks of any changes
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

#Creating databases tables on startup
@asynccontextmanager
async def database_lifespan(app: FastAPI):
    print("App is Starting.....")
    create_db_and_tables_in_sqlite()

    yield 
    
    print("App is Shutting Down.....")

app = FastAPI(lifespan=database_lifespan) 

@app.get("/")
def root():
    return {"message": "Hello World!"}

# @app.get("/heroes/")
# def read_heroes(session:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=10)] = 10) -> list[Hero]:
#     heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
#     return heroes
    
# @app.get("/heroes/{hero_id}")
# def read_hero(hero_id: int, session:SessionDep) -> Hero:
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero Not Found")
#     return hero

# @app.post("/heroes/")
# def create_hero(hero: Hero, session:SessionDep) -> Hero:
#     session.add(hero)
#     session.commit()
#     session.refresh(hero)
#     return hero

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session:SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero Not Found")
    session.delete(hero)
    session.commit()
    return {"message": f"{hero.hero_name} with ID{hero_id} has been deleted from the database."}

# With multiple models
@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes(session:SessionDep, offset:int = 0, limit: Annotated[int, Query(le=10)] = 10):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
    
@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session:SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero Not Found")
    return hero

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session:SessionDep) -> Hero:
    db_hero = Hero.model_validate(hero) #validate the created hero with the original Hero model
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero:HeroUpdate, session:SessionDep) -> Hero:
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero Not Found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

