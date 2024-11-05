import pytest
import sqlite3

from unittest.mock import patch, MagicMock

from meal_max.models.kitchen_model import Meal,create_meal,clear_meals


def test_meal_create():
    meal = Meal(id=1, meal="Pasta", cuisine="Italian", price=12.5, difficulty="MED")
    assert meal.meal == "Pasta"
    assert meal.cuisine == "Italian"
    assert meal.price == 12.5
    assert meal.difficulty == "MED"

def test_create_meal_invalid_price_type():
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Pizza", "Italian", "ten dollars", "MED")

def test_create_meal_negative_price():
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Pizza", "Italian", -10.0, "MED")

def test_create_meal_invalid_difficulty():
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        create_meal("Pizza", "Italian", 15.0, "any")

# def test_create_meal_duplicate_meal():
#     create_meal("Pasta", "Italian", 12.5, "MED")
#     with pytest.raises(ValueError, match="Meal with name 'Pasta' already exists"):
#             create_meal("Pasta", "Italian", 11.5, "MED")

def test_clear_meals():
    create_meal("Pizza", "Italian", 15.0, "MED")
    clear_meals()



