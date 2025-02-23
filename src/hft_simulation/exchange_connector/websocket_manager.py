from abc import ABC, abstractmethod

class WebsocketManager(ABC):
    '''
    Abstract class for managing WebSocket connections
    '''

    @abstractmethod
    def __ainit__(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def send(self, message: dict) -> None:
        pass

    @abstractmethod
    def receive(self) -> None:
        pass

    @abstractmethod
    def subscribe(self) -> None:
        pass