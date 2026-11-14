# --- acceptance_backfill (EVAL_ACCEPTANCE_STANDARD.md P4) ---
# 证据来源: .github/workflows/ci.yml
# 命令逐字取自该来源，未增删任何参数。
# 归一: python → python3（本机无 python 别名，实测 Error 127）
# 归一: 补解释器前缀。CI 在测试前 `python -m pip install -r backend/requirements-dev.txt`，
#   本机系统 python 是 PEP-668 外部管理环境（EXTERNALLY-MANAGED，pip 装不进去），
#   缺 python-jose / passlib / anthropic，61 项测试全在 fixture 处
#   ModuleNotFoundError: No module named 'jose'（不是测试失败）。
#   已在 ~/.cache/life-planner-venv 建好带依赖的环境（可复建）：
#     python3 -m venv --system-site-packages ~/.cache/life-planner-venv
#     ~/.cache/life-planner-venv/bin/python -m pip install -r backend/requirements-dev.txt
#   eval 在该解释器存在时用它，否则回退 python3（等价于 CI 装完依赖后的裸命令）。
PLANNER_PY := $(firstword $(wildcard $(HOME)/.cache/life-planner-venv/bin/python) python3)

.PHONY: eval

eval:
	$(PLANNER_PY) -m pytest -q
