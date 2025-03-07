from enum import Enum


class ActivationType(Enum):  
    Slot=0
    Timestamp=1

    def __str__(self) -> str:
        return f"{self.value[1]}"
    
    def __repr__(self) -> str:
        return self.name