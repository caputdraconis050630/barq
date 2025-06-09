import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from app.services.runtimes import get_runtime_handler
from app.registry.couchdb_registry import get_function_metadata, create_function_document
from app.registry.log_registry import save_execution_log
from app.models.function_model import FunctionCreateRequest
from app.services.warm_pool_manager import warm_pool_manager
import asyncio
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Functions storage 경로 (컨테이너 실행용 임시 파일들 저장)
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage") # /backend/storage

async def save_function(req: FunctionCreateRequest):
    """
    함수 메타데이터와 코드를 데이터베이스에 저장합니다.
    실제 코드는 DB에 저장되고, storage는 실행시에만 사용됩니다.
    """
    await create_function_document(req)
    
    # 함수 저장 후 미리 warm up 시도 (백그라운드)
    try:
        logger.info(f"Attempting warmup for function {req.func_id}")
        _try_warmup_function(req.func_id, req.runtime, req.entrypoint, req.code)
    except Exception as e:
        # warm up 실패는 로그만 남기고 계속 진행
        logger.warning(f"Failed to warm up function {req.func_id}: {e}")

def invoke_function(func_id: str, event: Dict[str, Any]) -> str:
    """
    저장된 함수를 실행하고 로그를 저장합니다.
    Warm pool을 우선 활용하고, 없으면 일반 실행합니다.
    
    Args:
        func_id: 실행할 함수 ID
        event: 함수에 전달할 이벤트 데이터
        
    Returns:
        함수 실행 결과 또는 에러 메시지
    """
    logger.info(f"Invoking function {func_id}")
    
    # 1. 함수 메타데이터 조회
    function_metadata = _get_function_metadata(func_id)
    
    # 2. Warm pool에서 컨테이너 확인
    logger.info(f"Checking warm pool for function {func_id}")
    warm_container_id = warm_pool_manager.get_warm_container(func_id)
    
    if warm_container_id:
        logger.info(f"Using warm container {warm_container_id} for function {func_id}")
        # 3-A. Warm 컨테이너에서 실행
        try:
            execution_result = _execute_warm_function(warm_container_id, function_metadata, event)
            
            if execution_result["success"]:
                # 성공적으로 실행되면 컨테이너를 풀에 반환
                logger.info(f"Warm execution successful, returning container {warm_container_id} to pool")
                warm_pool_manager.return_warm_container(warm_container_id)
            else:
                # warm 실행 실패시 컨테이너 정리하고 일반 실행으로 fallback
                logger.warning(f"Warm execution failed, cleaning up container {warm_container_id}")
                runtime_handler = get_runtime_handler(function_metadata.get("runtime"))
                runtime_handler.cleanup_warm(warm_container_id)
                warm_pool_manager.remove_container(warm_container_id)
                
                # 일반 실행으로 fallback
                func_path = _prepare_function_storage(func_id)
                execution_result = _execute_function(func_path, function_metadata, event)
        except Exception as e:
            # 예외 발생시에도 컨테이너 상태 정리
            logger.error(f"Exception during warm execution: {e}, cleaning up container {warm_container_id}")
            runtime_handler = get_runtime_handler(function_metadata.get("runtime"))
            runtime_handler.cleanup_warm(warm_container_id)
            warm_pool_manager.remove_container(warm_container_id)
            
            # 일반 실행으로 fallback
            func_path = _prepare_function_storage(func_id)
            execution_result = _execute_function(func_path, function_metadata, event)
    else:
        logger.info(f"No warm container available for function {func_id}, using cold execution")
        # 3-B. 일반 실행
        func_path = _prepare_function_storage(func_id)
        execution_result = _execute_function(func_path, function_metadata, event)
        
        # 실행 성공시 다음을 위해 warm up 시도
        if execution_result["success"]:
            try:
                logger.info(f"Cold execution successful, attempting warmup for next invocation")
                _try_warmup_function(func_id, function_metadata.get("runtime"), 
                                   function_metadata.get("entrypoint"), function_metadata.get("code"))
            except Exception:
                pass  # warm up 실패는 무시
    
    # 4. 로그 저장
    _save_execution_log(func_id, execution_result, event)
    
    return execution_result["result"]

def _get_function_metadata(func_id: str) -> Dict[str, Any]:
    """데이터베이스에서 함수 메타데이터를 조회합니다."""
    meta = asyncio.run(get_function_metadata(func_id))
    if meta is None:
        raise RuntimeError(f"Function {func_id} not found in registry")
    return meta

def _prepare_function_storage(func_id: str) -> str:
    """함수 실행을 위한 storage 디렉토리를 준비합니다."""
    func_path = os.path.join(BASE_DIR, func_id)
    os.makedirs(func_path, exist_ok=True)
    return func_path

def _execute_function(func_path: str, metadata: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    """
    함수를 일반 방식으로 실행하고 결과를 반환합니다.
    
    Returns:
        dict: {"result": str, "success": bool, "error": Optional[str]}
    """
    try:
        runtime = metadata.get("runtime")
        entrypoint = metadata.get("entrypoint") 
        code = metadata.get("code")
        
        # 런타임 핸들러로 함수 준비 및 실행
        runtime_handler = get_runtime_handler(runtime)
        runtime_handler.prepare(func_path, code, entrypoint)
        result = runtime_handler.run(func_path, event)
        
        return {
            "result": result,
            "success": True,
            "error": None
        }
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        return {
            "result": error_msg,
            "success": False, 
            "error": str(e)
        }

def _execute_warm_function(container_id: str, metadata: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Warm 컨테이너에서 함수를 실행하고 결과를 반환합니다.
    """
    try:
        runtime = metadata.get("runtime")
        runtime_handler = get_runtime_handler(runtime)
        
        if not runtime_handler.supports_warm_pool():
            raise RuntimeError(f"Runtime {runtime} does not support warm pool")
        
        logger.info(f"Executing function in warm container {container_id}")
        result = runtime_handler.run_warm(container_id, event)
        
        return {
            "result": result,
            "success": True,
            "error": None
        }
    except Exception as e:
        error_msg = f"Warm execution error: {str(e)}"
        logger.error(error_msg)
        return {
            "result": error_msg,
            "success": False,
            "error": str(e)
        }

def _try_warmup_function(func_id: str, runtime: str, entrypoint: str, code: str) -> None:
    """함수를 warm up 합니다 (실패해도 예외 발생 안함)."""
    try:
        runtime_handler = get_runtime_handler(runtime)
        
        if not runtime_handler.supports_warm_pool():
            logger.info(f"Runtime {runtime} does not support warm pool")
            return
        
        func_path = _prepare_function_storage(func_id)
        logger.info(f"Starting warmup for function {func_id}")
        container_id = runtime_handler.warmup(func_id, func_path, code, entrypoint)
        
        if container_id:
            warm_pool_manager.add_warm_container(func_id, runtime, container_id)
            logger.info(f"Successfully warmed up function {func_id} with container {container_id}")
        else:
            logger.warning(f"Warmup failed for function {func_id}: no container ID returned")
    except Exception as e:
        logger.error(f"Warmup failed for function {func_id}: {e}")

def _save_execution_log(func_id: str, execution_result: Dict[str, Any], event: Dict[str, Any]) -> None:
    """함수 실행 로그를 데이터베이스에 저장합니다."""
    asyncio.run(save_execution_log(
        func_id, 
        execution_result["result"], 
        execution_result["success"],
        event
    ))

def get_warm_pool_stats() -> Dict[str, Any]:
    """현재 warm pool 상태를 반환합니다."""
    stats = warm_pool_manager.get_stats()
    logger.info(f"Warm pool stats: {stats}")
    return stats


