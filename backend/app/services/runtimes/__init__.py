from .python_runtime import PythonRuntime
from .nodejs_runtime import NodejsRuntime
from .go_runtime import GoRuntime

def get_runtime_handler(runtime: str):
    if runtime.startswith("python"):
        return PythonRuntime()
    elif runtime.startswith("node"):
        return NodejsRuntime()
    elif runtime.startswith("go"):
        return GoRuntime()
    else:
        raise ValueError(f"Unsupported runtime: {runtime}")