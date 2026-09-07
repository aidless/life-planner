# Life Planner 收口 Makefile（P7-B5）
#
# 常用：
#   make test        跑 pytest（P6 基线：82 passed + 18 skipped 量级）
#   make check       一致性门禁全套（菜单 + 迁移漂移），漂移即红
#   make migrate     维护窗口专用：DATABASE_URL=... make migrate
#   make health      生产 4800 只读探活
#
# 约定：校验脚本一律以 backend/ 为 cwd 跑（scripts/ 下相对路径假设）；
# 生产 4800 启动仍走 create_all，migrate 只在 stamp head 后的维护窗口用。

PY := backend/venv/bin/python

.PHONY: help test check check-menu check-drift migrate health

help:
	@echo "test        pytest 全量（正式库零碰，见 backend/tests/conftest.py 隔离）"
	@echo "check       check-menu + check-drift"
	@echo "check-menu  manifests ↔ 前端路由/菜单一致性（backend/scripts/check_module_menu.py）"
	@echo "check-drift alembic-head ↔ create_all 列级 parity（backend/scripts/check_db_drift.py）"
	@echo "migrate     需显式传 DATABASE_URL，如 DATABASE_URL=sqlite:////path/to.db make migrate"
	@echo "health      curl 4800/api/health 只读探活"

test:
	$(PY) -m pytest -q

check: check-menu check-drift

check-menu:
	cd backend && ./venv/bin/python scripts/check_module_menu.py

check-drift:
	cd backend && ./venv/bin/python scripts/check_db_drift.py

ifndef DATABASE_URL
migrate:
	@echo "拒绝执行：必须显式指定 DATABASE_URL（防误写生产库）。"
	@echo "示例：DATABASE_URL=sqlite:////tmp/x.db make migrate"
	@exit 2
else
migrate:
	cd backend && $(CURDIR)/$(PY) -m alembic -c migrations/alembic.ini upgrade head
endif

health:
	curl -sf http://localhost:4800/api/health | head -c 300; echo
