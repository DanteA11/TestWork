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

breeds = {elem["breed"]["name"] for elem in new_cats}

cats_data_for_update = [
    {
        "color": "Обновленный цвет",
    },
    {
        "age": 100,
    },
    {
        "color": "Обновленный цвет 1",
        "description": "Обновленное описание",
    },
    {
        "breed": {"name": "Обновленная порода"}
    },
    {
        "description": "Обновленное описание1",
        "breed": {"name": "Обновленная порода1"}
    },
    {
        "color": "Обновленный цвет вместе",
        "age": 501,
        "description": "Обновленное описание вместе",
        "breed": {"name": "Обновленная порода вместе"}
    },
]
