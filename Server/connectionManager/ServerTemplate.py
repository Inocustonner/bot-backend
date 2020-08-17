from abc import ABC, abstractmethod

class ServerTemplate(ABC):
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def sendall(self):
        pass