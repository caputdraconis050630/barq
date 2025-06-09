
import json
import os
import time
from handler import main

print("WARM_CONTAINER_READY", flush=True)

# 이벤트 파일을 주기적으로 확인
while True:
    try:
        if os.path.exists("/app/event_input.json"):
            with open("/app/event_input.json", "r") as f:
                event_data = json.load(f)
            
            # 이벤트 파일 삭제 (처리됨을 표시)
            os.remove("/app/event_input.json")
            
            try:
                result = main(event_data)
                output = {"result": result, "status": "success"}
            except Exception as e:
                output = {"result": str(e), "status": "error"}
            
            # 결과를 파일에 저장
            with open("/app/event_output.json", "w") as f:
                json.dump(output, f)
                
        time.sleep(0.1)  # 100ms 대기
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        with open("/app/event_output.json", "w") as f:
            json.dump({"result": str(e), "status": "error"}, f)
