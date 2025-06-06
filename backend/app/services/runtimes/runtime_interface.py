from abc import ABC, abstractmethod
from typing import Dict, Any

class RuntimeInterface(ABC):
    
    @abstractmethod
    def prepare(self, func_path: str, code: str, entrypoint: str):
        pass

    @abstractmethod
    def run(self, func_path: str, event: Dict[str, Any], log_path: str) -> str:
        pass
