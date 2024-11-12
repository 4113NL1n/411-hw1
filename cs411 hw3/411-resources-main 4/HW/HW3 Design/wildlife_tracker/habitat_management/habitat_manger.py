from typing import Optional, List
from wildlife_tracker.habitat_managment.habitat import Habitat

class HabitatManager:

    def __init__(self) -> None:
        habitats: dict[int, Habitat] = {}

    def update_habitat_details(self, **kwargs: dict[str: Any]) -> None:
        pass

    def assign_animals_to_habitat(self, animals: List[Animal]) -> None:
        pass

    def get_animals_in_habitat(self) -> List[Animal]:
        pass

    def get_habitat_details(self) -> dict:
        pass
