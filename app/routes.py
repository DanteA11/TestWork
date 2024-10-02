from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import models
import schemas
from models.crud import add_starting_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await models.start_conn()
    await models.start_conn(drop_all=True)  # Для теста
    await add_starting_data()  # Для теста
    yield
    await models.stop_conn()


app = FastAPI(lifespan=lifespan, title="CatsApi")


@app.get("/breeds/", response_model=list[schemas.Breed], name="Породы")
async def get_breeds():
    """Возвращает список всех пород"""
    res = await models.get_all_breeds()
    return res


@app.get("/cats/", response_model=list[schemas.CatShort], name="Котята")
async def get_cats():
    """Возвращает список всех котят"""
    res = await models.get_all_cats()
    return res


@app.get("/cats/breeds/{breed}",
         response_model=list[schemas.CatShort], name="Фильтр котят")
async def get_cats_by_breed(breed: str, color: str = None, age: int = None):
    """
    Возвращает котят определенной породы.
    Позволяет отфильтровать их по возрасту или по цвету.
    """
    breed = breed.lower()
    if color:
        color = color.lower()
    res = await models.get_cats_with_filter(breed, color=color, age=age)
    return res


@app.get("/cats/{cat_id}", response_model=Optional[schemas.CatOut],
         name="Котенок", responses={404: {"model": schemas.Message}})
async def get_cat_by_id(cat_id: int):
    """Возвращает котенка по id"""
    res = await models.get_cat_by_id(cat_id)
    if res:
        return res
    return JSONResponse(status_code=404, content={"message": "Item not found"})


@app.post("/cats/", response_model=schemas.CatOut,
          status_code=201, name="Добавить котенка")
async def add_cat(cat: schemas.CatIn):
    """Добавляет нового котенка."""
    res = await models.add_cat(cat.model_dump())
    return res


@app.patch("/cats/{cat_id}", status_code=204,
           name="Изменить котенка", responses={404: {"model": schemas.Message}})
async def change_cat(cat_id: int, cat: schemas.UpdateCat):
    """Изменяет данные о котенке"""
    res = await models.update_cat(cat_id, cat.model_dump(exclude_none=True))
    if res:
        return
    return JSONResponse(status_code=404, content={"message": "Item not found"})


@app.delete("/cats/{cat_id}", status_code=204, name="Удалить котенка")
async def drop_cat(cat_id: int):
    """Удаляет данные о котенке."""
    await models.delete_cat(cat_id)
