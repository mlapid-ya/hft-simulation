from abc import ABC, abstractmethod

class MessageProcessor(ABC):

    def __init__(self, stream_name: str):
        self.stream_name: str = stream_name

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(stream_name={self.stream_name})"
    
    @abstractmethod
    async def __ainit__(self) -> None:
        pass
    
    @abstractmethod
    async def process_message(self, message: dict) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass