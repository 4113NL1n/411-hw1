import pytest
import requests

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats


@pytest.fixture
def battle_model():
    return BattleModel()
