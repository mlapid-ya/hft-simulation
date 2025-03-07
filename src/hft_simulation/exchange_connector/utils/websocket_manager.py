from abc import ABC, abstractmethod

class WebsocketManager(ABC):
    """
    Abstract class for managing WebSocket connections
    """

    @abstractmethod
    async def __ainit__(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def receive(self) -> None:
        pass

    @abstractmethod
    async def send(self, message: dict) -> None:
        pass

    @abstractmethod
    async def subscribe(self) -> None:
        pass