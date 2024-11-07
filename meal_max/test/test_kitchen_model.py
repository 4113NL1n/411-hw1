import pytest
import requests
import re
import sqlite3


from contextlib import contextmanager

from meal_max.models.kitchen_model import create_meal

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


def test_create_meal(mock_cursor):
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (0,)  
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    expected_query = normalize_whitespace(
        """INSERT INTO meals (meal, cuisine, price, difficulty) 
        VALUES (?, ?, ?, ?)
    """)
    assert actual_query == expected_query
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Pizza", "Italian", 12.5, "MED")
    assert actual_arguments == expected_arguments
    
def test_create_meal_invalid_price_type():
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Pizza", "Italian", "ten dollars", "MED")

def test_create_meal_negative_price():
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Pizza", "Italian", -10.0, "MED")

def test_create_meal_invalid_difficulty():
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        create_meal("Pizza", "Italian", 15.0, "any")
        
def test_create_meal_duplicates(mock_cursor):
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (0,)  
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    mock_cursor.execute.side_effect = sqlite3.IntegrityError()
    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal("Pizza", "Italian", 12.5, "MED")

def test_create_meal_database_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")