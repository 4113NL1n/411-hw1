import pytest
import requests
from contextlib import contextmanager

from meal_max.models.kitchen_model import Meal,create_meal

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  
    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)
    return mock_cursor 
    

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




