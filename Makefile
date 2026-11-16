# Offline checks. CI runs the same two targets from a fresh checkout
# after installing backend/requirements-dev.txt and frontend npm packages.
# Neither target calls Claude. ANTHROPIC_API_KEY and B4_INTEGRATION are
# removed for pytest so a developer key cannot change the result.
#
# PY defaults to python3. A local .venv is used when it exists:
#   python3 -m venv .venv && .venv/bin/pip install -r backend/requirements-dev.txt

PY ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

.PHONY: check check-backend check-frontend

check: check-backend check-frontend

check-backend:
	env -u ANTHROPIC_API_KEY -u B4_INTEGRATION $(PY) -m pytest -q
	$(PY) -m mypy --config-file pyproject.toml backend/app

check-frontend:
	cd frontend && npm run lint && npx tsc --noEmit && npm run build
