"""Recount OpenAPI operations and the default pytest result.

The numbers in the README honesty block are claims. This test recomputes
them. It does not invent a pass count: a child pytest process, with the
Claude key and the B4 opt-in removed, prints the summary that must match.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
AUTHOR_PATH = re.compile(r"F:[/\\]+life-planner")


def _honesty_block(text: str) -> dict[str, str]:
    match = re.search(r"<!-- honesty:start -->(.*)<!-- honesty:end -->", text, re.S)
    assert match, "README is missing the honesty block"
    found: dict[str, str] = {}
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        found[key.strip()] = value.strip()
    return found


def _openapi_counts() -> tuple[int, int]:
    backend = REPO / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    from app.main import app

    spec = app.openapi()
    paths = spec["paths"]
    operations = 0
    for item in paths.values():
        for method in item:
            if method.lower() in HTTP_METHODS:
                operations += 1
    return len(paths), operations


def _default_pytest_counts() -> tuple[int, int]:
    if os.environ.get("HONESTY_DRIFT_CHILD") == "1":
        return 0, 0
    env = os.environ.copy()
    env["HONESTY_DRIFT_CHILD"] = "1"
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("B4_INTEGRATION", None)
    tmp = tempfile.mkdtemp(prefix="honesty-drift-")
    env["DATABASE_URL"] = "sqlite:///" + str(Path(tmp) / "honesty.db")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=line", "-p", "no:cacheprovider"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    output = proc.stdout + "\n" + proc.stderr
    assert proc.returncode == 0, output[-4000:]
    match = None
    for line in output.splitlines():
        found = re.search(r"(\d+) passed(?:, (\d+) skipped)?", line)
        if found:
            match = found
    assert match, output[-2000:]
    passed = int(match.group(1))
    skipped = int(match.group(2) or 0)
    return passed, skipped


def _coming_soon_keys() -> list[str]:
    text = (REPO / "frontend/src/config/dimensionConfig.tsx").read_text(encoding="utf-8")
    keys: list[str] = []
    for match in re.finditer(r'key:\s*"([^"]+)"([\s\S]*?)status:\s*"([^"]+)"', text):
        if match.group(3) == "coming_soon":
            keys.append(match.group(1))
    return keys


def test_honesty_counts_match_tree() -> None:
    if os.environ.get("HONESTY_DRIFT_CHILD") == "1":
        return

    readme = README.read_text(encoding="utf-8")
    block = _honesty_block(readme)
    paths, operations = _openapi_counts()
    passed, skipped = _default_pytest_counts()
    modules = len(list((REPO / "backend/app/modules").glob("*/router.py")))
    coming = _coming_soon_keys()

    assert block["openapi_paths"] == str(paths)
    assert block["openapi_operations"] == str(operations)
    assert block["backend_modules"] == str(modules)
    assert int(block["tests_passed_default"]) == passed
    assert int(block["tests_skipped_default"]) == skipped
    assert int(block["tests_collected"]) == passed + skipped
    assert block["coming_soon_dimensions"] == "health,finance,habits"
    assert coming == ["health", "finance", "habits"]

    app_tsx = (REPO / "frontend/src/App.tsx").read_text(encoding="utf-8")
    for route in ('path="/health"', 'path="/finance"', 'path="/habits"'):
        assert route not in app_tsx

    assert "img.shields.io/badge/tests-" not in readme
    assert "img.shields.io/badge/mypy-" not in readme
    assert "lifeplanner" in readme
    assert "GitHub About" in readme
    for phrase in ("个人全栈", "不是经过验证", "不是生产", "医疗", "财务", "招生"):
        assert phrase in readme

    services = (REPO / "backend/app/modules/college/services.py").read_text(encoding="utf-8")
    assert "100_000" not in services
    assert "100000" not in services

    ai_client = (REPO / "backend/app/shared/ai_client.py").read_text(encoding="utf-8")
    assert "AI 分析服务未配置（缺少 ANTHROPIC_API_KEY）" in ai_client
    assert "if not self.enabled" in ai_client

    failure_modes = (REPO / "FAILURE_MODES.md").read_text(encoding="utf-8")
    for phrase in ("分数线", "幻觉", "示例数据", "SECRET_KEY", "verify_signature"):
        assert phrase in failure_modes

    compose = (REPO / "deploy/docker-compose.yml").read_text(encoding="utf-8")
    assert "backend:" in compose and "frontend:" in compose
    assert "sqlite:" in compose

    labeled_suffixes = {".py", ".md", ".ts", ".tsx", ".txt", ".yml", ".yaml"}
    for path in REPO.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in labeled_suffixes:
            continue
        if any(part in path.parts for part in (".git", "node_modules", ".venv", "dist")):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not AUTHOR_PATH.search(text):
            continue
        if path.name in {"README.md", "FAILURE_MODES.md"}:
            assert "AUTHOR_PATH" in text
            continue
        head = "\n".join(text.splitlines()[:30])
        assert "AUTHOR_PATH" in head, f"{path.relative_to(REPO)} has an unlabeled author Windows path"

    trust_bd = (REPO / "backend/app/middleware/trust_bd.py").read_text(encoding="utf-8")
    assert "AUTHOR_PATH" in trust_bd
    assert "verify_signature" in trust_bd
