from abc import ABC, abstractmethod


class BaseConnector(ABC):

    @abstractmethod
    def collect(self):
        pass

    @abstractmethod
    def synchronize(self):
        pass