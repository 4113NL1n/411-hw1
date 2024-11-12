import pytest
import requests
import re
import sqlite3
import logging
from unittest import mock
from contextlib import contextmanager
from meal_max.models.kitchen_model import Meal,create_meal,clear_meals,delete_meal,get_leaderboard,get_meal_by_id,get_meal_by_name,update_meal_stats
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
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    expected_query = normalize_whitespace(
        """INSERT INTO meals (meal, cuisine, price, difficulty) 
        VALUES (?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
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
def test_create_meal_zero_price():
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Pizza", "Italian", 0, "MED")
def test_create_meal_invalid_difficulty():
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        create_meal("Pizza", "Italian", 15.0, "any")  
def test_create_meal_duplicates(mock_cursor):
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    mock_cursor.execute.side_effect = sqlite3.IntegrityError()
    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal("Pizza", "Italian", 12.5, "MED")
def test_create_meal_database_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
def test_clear_meals(mocker,mock_cursor):
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))
    clear_meals()
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()
def test_clear_meal_empty(mock_cursor, mocker):
    mock_cursor.executescript.return_value = None
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))
    clear_meals()
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')
    mock_cursor.executescript.assert_called_once()
def test_clear_meals_database_error(mock_cursor,mocker):
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    mock_cursor.executescript.side_effect = sqlite3.Error("db err")
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_mel_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))
    with pytest.raises(sqlite3.Error, match="db err"):
        clear_meals()
def test_delete_meal(mock_cursor):
    mock_cursor.fetchone.return_value = ([False])
    delete_meal(1)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."
    expected_select_args = (1,)
    expected_update_args = (1,)
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."
def test_delete_meal_bad_id(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)
    with pytest.raises(ValueError, match="Meal with ID ""das"" not found"):
        delete_meal("das")        
def test_delete_meal_already_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = ([True])
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)
def test_delte_meal_database_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        delete_meal(1)    
# def test_get_leaderboard_wins(mock_cursor):
#     mock_cursor.fetchall = lambda: [
#         (0, "Pizza", "Italian", 100, "LOW", 100, 100, 1.0),
#         (1, "Pasta", "Italian", 101, "MED", 10, 2, 0.2),
#         (2, "Chicken", "Chinese", 102, "MED",20, 20, 1.0)
#     ]
#     meal = get_leaderboard(sort_by = "wins")  
#     expected_result = [
#         {'id': 0, 'meal': "Pizza", 'cuisine': "Italian", 'price': 100, 'difficulty': "LOW", 'battles': 100,'wins': 100, 'win_pct': 100}, 
#         {'id': 2, 'meal': "Chicken", 'cuisine': "Chinese", 'price': 102, 'difficulty': "MED", 'battles': 20, 'wins': 20, 'win_pct': 100},
#         {'id': 1, 'meal': "Pasta", 'cuisine': "Italian", 'price': 101, 'difficulty': "MED", 'battles': 10, 'wins': 2, 'win_pct': 20}
#     ]
#     assert meal == expected_result,f"Expected {expected_result}, but got {meal}"
#     expected_query = normalize_whitespace(""" 
#         SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
#         FROM meals
#         WHERE deleted = false AND battles > 0
#         ORDER BY wins DESC
#     """)
#     actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
#     assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_wins(mock_cursor):
    mock_cursor.fetchall.return_value = [
            (0, "Pizza", "Italian", 100, "LOW", 100, 100, 1.0),
            (2, "Chicken", "Chinese", 102, "MED",20, 20, 1.0),
            (1, "Pasta", "Italian", 101, "MED", 10, 2, 0.2)
        ]
    meal = get_leaderboard(sort_by="wins")

    expected_result = [
        {'id': 0, 'meal': "Pizza", 'cuisine': "Italian", 'price': 100, 'difficulty': "LOW", 'battles': 100, 'wins': 100, 'win_pct': 100},
        {'id': 2, 'meal': "Chicken", 'cuisine': "Chinese", 'price': 102, 'difficulty': "MED", 'battles': 20, 'wins': 20, 'win_pct': 100},
        {'id': 1, 'meal': "Pasta", 'cuisine': "Italian", 'price': 101, 'difficulty': "MED", 'battles': 10, 'wins': 2, 'win_pct': 20}
    ]
    assert meal == expected_result, f"Expected {expected_result}, but got {meal}"
def test_get_leaderboard_fail():
    with pytest.raises(ValueError, match="Invalid sort_by parameter: 12"):
        mealhuh = get_leaderboard(sort_by = 12)
    with pytest.raises(ValueError, match="Invalid sort_by parameter: fefew"):
        mealhuh = get_leaderboard(sort_by = "fefew")    
def test_get_leaderboard_database_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        get_leaderboard("wins")    
    with pytest.raises(sqlite3.Error, match="database error"):
        get_leaderboard("win_pct")    
def test_get_meal_by_id(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 100, "LOW",False)
    result = get_meal_by_id(1)
    expected_result = Meal(1, "Pizza","Italian", 100,"LOW")
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")    
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
def test_get_meal_by_id_deleted_id(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 100, "LOW",True)
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        result = get_meal_by_id(1)
def test_get_meal_by_id_fail_id_None(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        result = get_meal_by_id(1)
def test_get_meal_by_id_fail_id_With(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 100, "LOW",False)
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        result = get_meal_by_id(2)
def test_get_meal_by_name(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 100, "LOW",False)
    result = get_meal_by_name("Pizza")
    expected_result = Meal(1, "Pizza","Italian", 100,"LOW")
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")    
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ('Pizza',)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
def test_get_meal_by_name_deleted_id(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 100, "LOW",True)
    with pytest.raises(ValueError, match="Meal with name Pizza has been deleted"):
        result = get_meal_by_name("Pizza")
def test_get_meal_by_id_fail_id_None(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with name Pizza not found"):
        result = get_meal_by_name("Pizza")
def test_get_meal_by_id_fail_id_With(mock_cursor):
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 100, "LOW",False)
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        result = get_meal_by_name("Pasta")
def test_update_meal_stats(mock_cursor):
    mock_cursor.fetchone.return_value = [False]
    meal_id = 1
    update_meal_stats(meal_id,"win")
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
def test_update_meal_stats_deleted(mock_cursor):
    mock_cursor.fetchone.return_value = [True]
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1,"wins")
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))
def test_update_meal_stats_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        update_meal_stats(1,"wins")
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))
def test_update_meal_stats_invalid_value(mock_cursor):
    mock_cursor.fetchone.return_value = [False]
    meal_id = 1
    with pytest.raises(ValueError, match="Invalid result: winning. Expected 'win' or 'loss'."):
        update_meal_stats(meal_id,"winning")
def test_update_meal_stats_database_error(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.Error("database error")
    with pytest.raises(sqlite3.Error, match="database error"):
        update_meal_stats(1,"win")    