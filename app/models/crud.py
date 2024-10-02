from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from .models import Base, Cat, Breed
from .database import session

__all__ = [
    "get_all_cats", "get_all_breeds", "get_cat_by_id",
    "get_cats_with_filter", "update_cat", "delete_cat",
    "Base", "add_cat"
]


async def __get_all(elem: type[Base]):
    res = await session.execute(select(elem))
    return res.scalars().all()


async def __check_breed(breed_name: str):
    breed = await session.execute(
        select(Breed).filter(Breed.name == breed_name)
    )
    breed = breed.scalars().first()
    return breed


async def get_all_cats():
    """Возвращает список всех котят."""
    return await __get_all(Cat)


async def get_all_breeds():
    """Возвращает список всех пород"""
    return await __get_all(Breed)


async def add_cat(cat: dict):
    """Добавляет котенка в БД."""
    n_breed = cat.pop("breed")["name"]
    check = 0
    async with session.begin_nested():
        new_cat = Cat(**cat)
        new_cat.breed = n_breed
        try:
            session.add(new_cat)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            check = 1

    if not check:
        return new_cat

    breed = await __check_breed(breed_name=n_breed)
    async with session.begin_nested():
        new_cat.breed = breed
        session.add(new_cat)
        await session.commit()

    return new_cat


async def get_cats_with_filter(breed: str, *, color: str = None, age: int = None):
    """
    Возвращает список котиков, подходящих под условия.

    :param breed: Порода
    :param color: Цвет
    :param age: Возраст
    """
    query = select(Cat).filter(Cat.breed.has(name=breed))
    if color is not None:
        query = query.filter(Cat.color == color)
    if age is not None:
        query = query.filter(Cat.age == age)
    res = await session.execute(
        query
    )
    return res.scalars().all()


async def get_cat_by_id(cat_id: int):
    """Возвращает котенка по id."""
    res = await session.execute(
        select(Cat).filter(Cat.id == cat_id)
    )
    return res.scalars().first()


async def update_cat(cat_id: int, data: dict):
    """Обновляет информацию о котенке."""
    cat = await get_cat_by_id(cat_id)
    if not cat or not data:
        return False
    breed = data.pop("breed", {})
    check = 0
    async with session.begin_nested():
        for k, v in data.items():
            setattr(cat, k, v)
        if breed:
            try:
                br = Breed(name=breed['name'])
                cat.breed = br
                await session.commit()
            except IntegrityError:
                await session.rollback()
                check = 1
        else:
            await session.commit()

    if not check:
        return True

    breed = await __check_breed(breed_name=breed["name"])
    async with session.begin_nested():
        await session.refresh(cat)
        cat.breed = breed
        await session.commit()

    return True


async def delete_cat(cat_id: int):
    """Удаляет информацию о котенке"""
    await session.execute(
        delete(Cat).filter(Cat.id == cat_id)
    )
    await session.commit()


async def add_starting_data():
    new_cats = [
        {
            "color": "Серый",
            "age": 3,
            "description": "Киска с мягкими лапками",
            "breed": {"name": "Чеширский"}
        },
        {
            "color": "Черный",
            "age": 2,
            "description": "Суетливая дымка",
            "breed": {"name": "Британский"}
        },
        {
            "color": "Белый",
            "age": 5,
            "description": "Голубоглазая киса",
            "breed": {"name": "Чеширский"}
        },
        {
            "color": "Серый",
            "age": 5,
            "description": "Тыгыдык, тыгыдык",
            "breed": {"name": "Чеширский"}
        },
        {
            "color": "Рыжий",
            "age": 2,
            "description": "Ни Хао Ма",
            "breed": {"name": "Китайский"}
        }
    ]
    for cat in new_cats:
        await add_cat(cat)
