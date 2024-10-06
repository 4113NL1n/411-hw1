from typing import Any, Optional
class Animal:

    def __init__(self,
                    animal_id: int,
                    species: str,
                    size: int,
                    current_location: str,
                    age: Optional[int] = None,
                    health_status: Optional[str] = None
        

                    ) -> None:
        
        def get_animal_details(animal_id) -> dict[str, Any]:
            pass
        def update_animal_details(animal_id: int, **kwargs: Any) -> None:
            pass
