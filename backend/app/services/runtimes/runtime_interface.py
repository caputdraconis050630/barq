from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class RuntimeInterface(ABC):
    
    @abstractmethod
    def prepare(self, func_path: str, code: str, entrypoint: str):
        """함수 실행을 위한 코드와 설정 파일을 storage에 준비합니다."""
        pass

    @abstractmethod
    def run(self, func_path: str, event: Dict[str, Any]) -> str:
        """준비된 함수를 실행하고 결과를 반환합니다."""
        pass
    
    def warmup(self, func_id: str, func_path: str, code: str, entrypoint: str) -> Optional[str]:
        """
        함수를 미리 warm up합니다. 
        반환값: warm container ID 또는 None (warm pool 미지원시)
        """
        return None
    
    def run_warm(self, container_id: str, event: Dict[str, Any]) -> str:
        """
        warm up된 컨테이너에서 함수를 실행합니다.
        기본 구현은 일반 run 메소드를 호출합니다.
        """
        raise NotImplementedError("Warm pool not supported for this runtime")
    
    def cleanup_warm(self, container_id: str) -> None:
        """warm up된 컨테이너를 정리합니다."""
        pass
    
    def supports_warm_pool(self) -> bool:
        """이 런타임이 warm pool을 지원하는지 반환합니다."""
        return False
