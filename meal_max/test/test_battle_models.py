import pytest
import requests

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal,create_meal

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


def test_prep_combatant_success(battle_model, sampleMeal_1, sampleMeal_2):
    battle_model.prep_combatant(sampleMeal_1)
    assert battle_model.combatants == [sampleMeal_1]
    battle_model.prep_combatant(sampleMeal_2)
    assert battle_model.combatants == [sampleMeal_1, sampleMeal_2]    

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

def test_battle(battle_model,sampleMeal_1,sampleMeal_3):
    battle_model.prep_combatant(sampleMeal_1)
    battle_model.prep_combatant(sampleMeal_3)
    winner = battle_model.battle()
    assert winner == battle_model.combatants[0].meal 
    