import pytest
from fastapi.testclient import TestClient

from tests.data import new_cats, breeds, cats_data_for_update
from routes import app

client = TestClient(app)


@pytest.mark.usefixtures("create_and_drop_tables")
class TestApp:
    def test_get_all_breeds_before_adding(self):
        response = client.get("/breeds")
        assert response.status_code == 200
        res = response.json()
        assert res == []

    def test_get_all_cats_before_adding(self):
        response = client.get("/cats")
        assert response.status_code == 200
        res = response.json()
        assert res == []

    def test_get_cat_by_id_before_adding(self):
        response = client.get("/cats/1")
        assert response.status_code == 404
        res = response.json()
        assert "message" in res

    def test_get_cat_by_id_negative(self):
        response = client.get("/cats/negative")
        assert response.status_code == 422
        res = response.json()
        assert "detail" in res

    @pytest.mark.parametrize("cat", new_cats)
    def test_add_cat(self, cat):
        response = client.post("/cats", json=cat)
        assert response.status_code == 201
        res = response.json()
        response = client.get(f"/cats/{res['id']}")
        new_res = response.json()
        assert res == new_res

    @pytest.mark.parametrize("cat", cats_data_for_update)  # Пойдут как негативные данные.
    def test_add_cat_negative(self, cat):
        response = client.post("/cats", json=cat)
        assert response.status_code == 422
        res = response.json()
        assert "detail" in res

    def test_get_all_breeds_after_adding(self):
        response = client.get("/breeds")
        assert response.status_code == 200
        res = response.json()
        assert len(res) == len(breeds)

    def test_get_all_cats_after_adding(self):
        response = client.get("/cats")
        assert response.status_code == 200
        res = response.json()
        assert len(res) == len(new_cats)

    def test_get_cat_by_id_after_adding(self):
        response = client.get("/cats/1")
        assert response.status_code == 200
        cat = response.json()
        assert isinstance(cat, dict)

        for k, v in new_cats[0].items():
            res = cat[k]
            assert isinstance(res, type(v))

    @pytest.mark.parametrize(
        "breed, amount", [
            ("Чеширский", 3), ("Британский", 1),
            ("Китайский", 1), ("Японский", 0)
        ]
    )
    def test_get_cats_with_filter_only_breed(self, breed, amount):
        response = client.get(f"/cats/breeds/{breed}")
        assert response.status_code == 200
        res = response.json()
        assert len(res) == amount

    @pytest.mark.parametrize(
        "breed, amount, color",
        [("Чеширский", 2, "Серый"),
         ("Чеширский", 1, "Белый"),
         ("Китайский", 0, "Зеленый")]
    )
    def test_get_cats_with_filter_breed_color(self, breed, amount, color):
        response = client.get(f"/cats/breeds/{breed}?color={color}")
        assert response.status_code == 200
        res = response.json()
        assert len(res) == amount

    @pytest.mark.parametrize(
        "breed, amount, age",
        [("Чеширский", 2, 5), ("Чеширский", 1, 3),
         ("Британский", 1, 2), ("Британский", 0, 3)]
    )
    def test_get_cats_with_filter_breed_age(self, breed, amount, age):
        response = client.get(f"/cats/breeds/{breed}?age={age}")
        assert response.status_code == 200
        res = response.json()
        assert len(res) == amount

    @pytest.mark.parametrize(
        "breed, amount, color, age",
        [("Чеширский", 1, "Серый", 5),
         ("Британский", 1, "Черный", 2),
         ("Британский", 0, "Белый", 2)]
    )
    def test_get_cats_with_all_filter(self, breed, amount, color, age):
        response = client.get(f"/cats/breeds/{breed}?color={color}&age={age}")
        assert response.status_code == 200
        res = response.json()
        assert len(res) == amount

    def test_get_cats_with_filter_negative(self):
        response = client.get("/cats/breeds/Чеширский?age=asd")
        assert response.status_code == 422
        res = response.json()
        assert "detail" in res

    @pytest.mark.parametrize("data", cats_data_for_update[:-1])
    def test_update_cat(self, data: dict):
        response = client.patch("/cats/1", json=data)
        assert response.status_code == 204

        response = client.get("/cats/1")
        res = response.json()

        for k, v in data.items():
            if isinstance(v, str):
                v = v.lower()
            if isinstance(v, dict):
                v = {k_.lower(): v_.lower() for k_, v_ in v.items()}
            elem = res[k]
            assert elem == v

    @pytest.mark.parametrize("key, value", [
        ("age", 305), ("color", "a" * 31),
        ("description", "a" * 151), ("breed", {"name": "a" * 101})
    ])
    def test_update_cat_negative_data(self, key, value):
        response = client.patch('/cats/1', json={key: value})
        assert response.status_code == 422
        res = response.json()
        assert "detail" in res

    def test_update_cat_negative_parameter(self):
        response = client.patch('/cats/1', json={"name": "lalala"})
        assert response.status_code == 404
        res = response.json()
        assert "message" in res

    def test_update_cat_with_id_more_max(self):
        response = client.patch('/cats/150', json={"age": 5})
        assert response.status_code == 404
        res = response.json()
        assert "message" in res

    def test_delete_cat(self):
        response = client.get("/cats")
        cats = response.json()
        length = len(cats)
        response = client.delete("/cats/1")
        assert response.status_code == 204

        response = client.get("/cats")
        cats = response.json()
        assert len(cats) == length - 1

        for cat in cats:
            response = client.delete(f"/cats/{cat['id']}")
            assert response.status_code == 204

        response = client.get("/cats")
        cats = response.json()
        assert cats == []
