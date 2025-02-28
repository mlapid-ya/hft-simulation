from abc import ABC, abstractmethod

class OnlineModel(ABC):
    """
    Abstract class for online classification models.
    """

    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def fit(self, X: dict[str, float], y: int) -> None:
        pass

    @abstractmethod
    def predict(self, X: dict[str, float]) -> int | None:
        pass

    def __repr__(self) -> str:
        return self.__str__()