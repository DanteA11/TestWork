import pytest

from tests.data import new_cats, breeds, cats_data_for_update
import models
from models.models import Cat


@pytest.mark.usefixtures("create_and_drop_tables_async")
class TestCrud:

    @pytest.mark.anyio
    async def test_get_all_cats_before_adding(self):
        res = await models.get_all_cats()
        assert res == []

    @pytest.mark.anyio
    async def test_get_all_breeds_before_adding(self):
        res = await models.get_all_breeds()
        assert res == []

    @pytest.mark.anyio
    async def test_get_cat_by_id_before_adding(self):
        res = await models.get_cat_by_id(1)
        assert res is None

    @pytest.mark.anyio
    @pytest.mark.parametrize("cat", new_cats)
    async def test_add_cat(self, cat: dict):
        res = await models.add_cat(cat)
        new_res = await models.get_cat_by_id(res.id)
        assert res == new_res

    @pytest.mark.anyio
    async def test_get_all_cats_after_adding(self):
        res = await models.get_all_cats()
        length = len(res)
        assert length == len(new_cats)

    @pytest.mark.anyio
    async def test_get_all_breeds_after_adding(self):
        res = await models.get_all_breeds()
        length = len(res)
        assert length == len(breeds)

    @pytest.mark.anyio
    async def test_get_cat_by_id_after_adding(self):
        res = await models.get_cat_by_id(1)
        assert isinstance(res, Cat)

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "breed, amount", [
            ("Чеширский", 3), ("Британский", 1),
            ("Китайский", 1), ("Японский", 0)
        ]
    )
    async def test_get_cats_with_filter_only_breed(self, breed, amount):
        res = await models.get_cats_with_filter(breed)
        assert len(res) == amount

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "breed, amount, color",
        [("Чеширский", 2, "Серый"),
         ("Чеширский", 1, "Белый"),
         ("Китайский", 0, "Зеленый")]
    )
    async def test_get_cats_with_filter_breed_color(self, breed, amount, color):
        res = await models.get_cats_with_filter(breed, color=color)
        assert len(res) == amount

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "breed, amount, age",
        [("Чеширский", 2, 5), ("Чеширский", 1, 3),
         ("Британский", 1, 2), ("Британский", 0, 3)]
    )
    async def test_get_cats_with_filter_breed_age(self, breed, amount, age):
        res = await models.get_cats_with_filter(breed, age=age)
        assert len(res) == amount

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "breed, amount, color, age",
        [("Чеширский", 1, "Серый", 5),
         ("Британский", 1, "Черный", 2),
         ("Британский", 0, "Белый", 2)]
    )
    async def test_get_cats_with_all_filter(self, breed, amount, color, age):
        res = await models.get_cats_with_filter(breed, color=color, age=age)
        assert len(res) == amount

    @pytest.mark.anyio
    @pytest.mark.parametrize("data", cats_data_for_update)
    async def test_update_cat(self, data: dict):
        await models.update_cat(1, data)
        res = await models.get_cat_by_id(1)
        for k, v in data.items():
            elem = getattr(res, k)
            assert elem == v

    @pytest.mark.anyio
    async def test_delete_cat(self):
        cats = await models.get_all_cats()
        length = len(cats)
        await models.delete_cat(1)
        cats = await models.get_all_cats()
        assert len(cats) == length - 1

        for cat in cats:
            await models.delete_cat(cat.id)
        cats = await models.get_all_cats()
        assert cats == []
