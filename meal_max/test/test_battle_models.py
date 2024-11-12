import pytest
import requests
import re
from contextlib import contextmanager
from meal_max.models.battle_model import BattleModel
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
     
@pytest.fixture
def battle_model():
    return BattleModel()
@pytest.fixture
def sampleMeal_1():
    return Meal(id=0, meal="Pasta", cuisine="Italian", price=12.5, difficulty="MED")
@pytest.fixture
def sampleMeal_2():
    return Meal(id=1, meal="Pizza", cuisine="Chinese", price=2.5, difficulty="LOW")
@pytest.fixture
def sampleMeal_3():
    return Meal(id=2, meal="Chinese", cuisine="English", price=25, difficulty="MED")

# There are only six test
def test_prep_combatant_success(battle_model, sampleMeal_1, sampleMeal_2,mock_cursor):
    battle_model.prep_combatant(sampleMeal_1)
    assert battle_model.combatants == [sampleMeal_1]
    battle_model.prep_combatant(sampleMeal_2)
    assert battle_model.combatants == [sampleMeal_1, sampleMeal_2]   
    #Not sure if needed, just in case
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (0,)  
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    create_meal(meal="Pasta", cuisine="Chinese", price=2.5, difficulty="LOW") 

def test_prep_combatant_full(battle_model, sampleMeal_1, sampleMeal_2, sampleMeal_3):
    battle_model.prep_combatant(sampleMeal_1)
    battle_model.prep_combatant(sampleMeal_2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sampleMeal_3)
        
        
def test_get_combatants(battle_model, sampleMeal_1, sampleMeal_2):
    battle_model.prep_combatant(sampleMeal_1)
    battle_model.prep_combatant(sampleMeal_2)
    assert battle_model.combatants == battle_model.get_combatants()
    assert len(battle_model.combatants) == 2
    assert battle_model.combatants[0].meal == "Pasta"  
    assert battle_model.combatants[1].meal == "Pizza" 
    assert battle_model.combatants == [sampleMeal_1, sampleMeal_2]    
   

def test_get_score(battle_model,sampleMeal_1,sampleMeal_3):
    battle_model.prep_combatant(sampleMeal_1)
    battle_model.prep_combatant(sampleMeal_3)
    score = (12.5 * 7 ) - 2
    assert battle_model.get_battle_score(sampleMeal_1) == score
    score2 = (25 * 7) - 2
    assert battle_model.get_battle_score(sampleMeal_3) == score2


def test_clear_combatants(battle_model,sampleMeal_1,sampleMeal_3):
    battle_model.prep_combatant(sampleMeal_1)
    battle_model.prep_combatant(sampleMeal_3)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0
    battle_model.prep_combatant(sampleMeal_1)
    assert len(battle_model.combatants) == 1
    
# Only one that need mock DB
def test_battle(mock_cursor,sampleMeal_1,sampleMeal_2,battle_model):
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (0,)  
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    create_meal(meal="Pasta", cuisine="Chinese", price=2.5, difficulty="LOW")
    battle_model.prep_combatant(sampleMeal_1)
    battle_model.prep_combatant(sampleMeal_2)
    winner = battle_model.battle()
    assert winner == battle_model.combatants[0].meal
    assert len(battle_model.combatants) == 1

def test_battle_failure(mock_cursor,sampleMeal_2,battle_model):
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (0,)  
    create_meal(meal="Pizza", cuisine="Italian", price=12.5, difficulty="MED")
    battle_model.prep_combatant(sampleMeal_2)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        winner = battle_model.battle()
    