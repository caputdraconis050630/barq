
import json
import sys
import time
from handler import main

print("WARM_CONTAINER_READY", flush=True)

while True:
    try:
        # stdin에서 이벤트 읽기 대기
        line = sys.stdin.readline()
        if not line:
            break
            
        event_data = json.loads(line.strip())
        result = main(event_data)
        print(json.dumps({"result": result, "status": "success"}), flush=True)
        
    except Exception as e:
        print(json.dumps({"result": str(e), "status": "error"}), flush=True)
    except KeyboardInterrupt:
        break
