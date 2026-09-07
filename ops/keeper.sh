#!/bin/bash
# life-planner keeper: ensure backend(:4800) is alive.
# 架构说明(P2-1): 后端同源托管 frontend/dist, /api 直通。
# 独立 serve 不能代理 /api, 其页面调数必坏, 故 P3-2 起退役 5173/8080,
# 只保活后端 4800(single origin)。
# Usage: keeper.sh [check|start-all]   (default: check)
set -u
RP="/data3/projects/life-planner"
VENV="$RP/backend/venv/bin/python"
BACKEND_PORT=4800
RUN_DIR="$HOME/.cache/life-planner"
LOGB="$RP/backend/backend.log"
mkdir -p "$RUN_DIR"

port_open() { python3 -c "import socket,sys; s=socket.socket(); s.settimeout(2); sys.exit(0 if s.connect_ex(('127.0.0.1',$1))==0 else 1)"; }

start_backend() {
  cd "$RP/backend"
  nohup "$VENV" -m uvicorn app.main:app --host 127.0.0.1 --port $BACKEND_PORT >>"$LOGB" 2>&1 &
  echo $! > "$RUN_DIR/backend.pid"
}

case "${1:-check}" in
  start-all|check)
    port_open $BACKEND_PORT || { start_backend; sleep 5; }
    ;;
esac
port_open $BACKEND_PORT && echo "keeper: backend=up" || echo "keeper: backend=down"
