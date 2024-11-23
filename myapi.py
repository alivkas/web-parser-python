import asyncio

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from parser import get_prices
from starlette.concurrency import run_in_threadpool
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlalchemy.orm import Session


app = FastAPI()
PRICES_DB = []


class Prices(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    cost: int


sqlite_url = "sqlite:///parser.db"
engine = create_engine(sqlite_url)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Depends(get_session)


class Item(BaseModel):
    ...


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_item(title, price, session: Session):
    item = Prices(name=title, cost=int(price.replace(' ', '').replace('₽', '')))
    session.add(item)
    session.commit()
    session.refresh(item)


async def background_parser_async():
    while True:
        print("Starting get price")
        products = await run_in_threadpool(get_prices)
        with Session(engine) as session:
            for title, price in products.items():
                print(f"{title} - {price}")
                add_item(title, price, session)
        await asyncio.sleep(12 * 60 * 60)


def background_add_item():
    data = get_prices()
    add_item(*data)


@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    asyncio.create_task(background_parser_async())


@app.get("/start_parser")
async def start_parser(background_tasks: BackgroundTasks):
    #  asyncio.create_task(background_add_item())
    background_tasks.add_task(background_add_item)
    return {}


@app.get("/prices")
async def read_prices(session: Session = SessionDep, offset: int = 0, limit: int = 1000):
    return session.execute(select(Prices).offset(offset).limit(limit)).scalars().all()


@app.get("/prices/{item_id}")
async def read_item(item_id: int, session: Session = SessionDep):
    price = session.get(Prices, item_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    return price


@app.put("/prices/{item_id}")
async def update_item(item_id: int, data: Prices, session: Session = SessionDep):
    price_db = session.get(Prices, item_id)
    if not price_db:
        raise HTTPException(status_code=404, detail="Price not found")
    price_data = data.model_dump(exclude_unset=True)
    price_db.sqlmodel_update(price_data)
    session.add(price_db)
    session.commit()
    session.refresh(price_db)
    return price_db


@app.post("/prices/create")
async def create_item(item: Prices, session: Session = SessionDep):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.delete("/prices/{item_id}")
async def delete_item(item_id: int, session: Session = SessionDep):
    price = session.get(Prices, item_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
    session.delete(price)
    session.commit()
    return {"ok": True}