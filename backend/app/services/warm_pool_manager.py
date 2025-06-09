import time
import threading
from typing import Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import logging
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class WarmContainer:
    container_id: str
    func_id: str
    runtime: str
    created_at: float
    last_used: float
    use_count: int = 0
    in_use: bool = False  # 현재 사용 중인지 여부

class WarmPoolManager:
    """
    Warm Pool을 관리하는 매니저 클래스
    - 함수별로 미리 준비된 컨테이너를 관리
    - TTL 기반 자동 정리
    - 사용 빈도 기반 우선순위 관리
    """
    
    def __init__(self, max_containers: int = 10, ttl_seconds: int = 300):
        self.max_containers = max_containers
        self.ttl_seconds = ttl_seconds # 기본 5분
        self.containers: Dict[str, WarmContainer] = {}  # container_id -> WarmContainer
        self.func_containers: Dict[str, list] = defaultdict(list)  # func_id -> [container_ids]
        self.lock = threading.Lock()
        
        # TTL 정리를 위한 백그라운드 스레드
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self._cleanup_thread.start()
    
    def get_warm_container(self, func_id: str) -> Optional[str]:
        """함수를 위한 사용 가능한 warm 컨테이너를 반환합니다."""
        with self.lock:
            if func_id in self.func_containers:
                # 사용 가능한 컨테이너 찾기
                for container_id in self.func_containers[func_id]:
                    if container_id in self.containers:
                        container = self.containers[container_id]
                        if not container.in_use:  # 사용 중이 아닌 컨테이너
                            container.last_used = time.time()
                            container.use_count += 1
                            container.in_use = True  # 사용 중으로 표시
                            logger.info(f"Using warm container {container_id} for function {func_id}")
                            return container_id
            
            return None
    
    def return_warm_container(self, container_id: str) -> bool:
        """사용 완료된 warm 컨테이너를 풀에 반환합니다."""
        with self.lock:
            if container_id in self.containers:
                container = self.containers[container_id]
                container.in_use = False  # 사용 가능 상태로 변경
                container.last_used = time.time()
                logger.info(f"Returned warm container {container_id} to pool")
                return True
            return False
    
    def add_warm_container(self, func_id: str, runtime: str, container_id: str) -> bool:
        """새로운 warm 컨테이너를 풀에 추가합니다."""
        with self.lock:
            if len(self.containers) >= self.max_containers:
                # 오래된 컨테이너 정리
                self._evict_oldest_container()
            
            now = time.time()
            warm_container = WarmContainer(
                container_id=container_id,
                func_id=func_id,
                runtime=runtime,
                created_at=now,
                last_used=now,
                in_use=False  # 초기에는 사용 가능 상태
            )
            
            self.containers[container_id] = warm_container
            self.func_containers[func_id].append(container_id)
            
            logger.info(f"Added warm container {container_id} for function {func_id}")
            return True
    
    def remove_container(self, container_id: str) -> bool:
        """컨테이너를 풀에서 제거하고 실제 Docker 컨테이너도 정리합니다."""
        with self.lock:
            if container_id in self.containers:
                container = self.containers.pop(container_id)
                if container.func_id in self.func_containers:
                    try:
                        self.func_containers[container.func_id].remove(container_id)
                        if not self.func_containers[container.func_id]:
                            del self.func_containers[container.func_id]
                    except ValueError:
                        pass
                
                # 실제 Docker 컨테이너도 정리
                self._cleanup_docker_container(container_id)
                
                logger.info(f"Removed warm container {container_id}")
                return True
            return False
    
    def _cleanup_docker_container(self, container_id: str) -> None:
        """실제 Docker 컨테이너를 정리합니다."""
        try:
            subprocess.run(["docker", "rm", "-f", container_id], 
                         capture_output=True, text=True, timeout=10)
            logger.info(f"Docker container {container_id} cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Docker container {container_id}: {e}")
    
    def _evict_oldest_container(self) -> None:
        """가장 오래되고 사용 중이 아닌 컨테이너를 제거합니다."""
        if not self.containers:
            return
        
        # 사용 중이 아닌 컨테이너들 중에서 가장 오래된 것 선택
        available_containers = [
            (cid, container) for cid, container in self.containers.items() 
            if not container.in_use
        ]
        
        if available_containers:
            oldest_id = min(available_containers, key=lambda x: x[1].last_used)[0]
            self.remove_container(oldest_id)
    
    def _cleanup_expired(self) -> None:
        """TTL이 만료된 컨테이너들을 정리합니다."""
        while True:
            try:
                time.sleep(30)  # 30초마다 정리
                now = time.time()
                expired_containers = []
                
                with self.lock:
                    for container_id, container in self.containers.items():
                        # 사용 중이 아니고 TTL이 만료된 컨테이너만 정리
                        if not container.in_use and now - container.last_used > self.ttl_seconds:
                            expired_containers.append(container_id)
                
                if expired_containers:
                    logger.info(f"Cleaning up {len(expired_containers)} expired containers")
                    
                for container_id in expired_containers:
                    self.remove_container(container_id)
                    
            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """현재 warm pool 상태를 반환합니다."""
        with self.lock:
            total_containers = len(self.containers)
            in_use_containers = sum(1 for c in self.containers.values() if c.in_use)
            available_containers = total_containers - in_use_containers
            
            return {
                "total_containers": total_containers,
                "available_containers": available_containers,
                "in_use_containers": in_use_containers,
                "max_containers": self.max_containers,
                "ttl_seconds": self.ttl_seconds,
                "functions_with_warm_containers": len(self.func_containers),
                "containers_by_function": {
                    func_id: {
                        "total": len(container_ids),
                        "available": sum(1 for cid in container_ids 
                                       if cid in self.containers and not self.containers[cid].in_use),
                        "in_use": sum(1 for cid in container_ids 
                                    if cid in self.containers and self.containers[cid].in_use)
                    }
                    for func_id, container_ids in self.func_containers.items()
                }
            }

# 전역 warm pool 매니저 인스턴스
warm_pool_manager = WarmPoolManager() 