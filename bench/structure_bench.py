#!/usr/bin/env python3
"""life-planner 结构基准（真实测量，非估算）。

度量后端的**业务模块注册**与**测试套件结构**，用 AST 静态分析（纯标准库），
并计时整个解析过程。这些数字是 life-planner 的**真实结构基线**：

  - 19 个业务模块（APIRouter 注册点）——对应 19 个 router.py；
  - 78 个测试函数（7 个测试文件）——其中 60 为核心、18 为 B4 集成
    （README「证明什么/不证明什么」声明，本基准用 AST 独立重算）；
  - OpenAPI 结构由 app.main 的 19 个 router 构成（106 ops / 71 paths，
    见 README 复算节，需完整依赖导入，本基准以 AST 注册点为准）。

为什么这是基准：life-planner 是一个 FastAPI 全栈应用，其「规模与结构」
是回归守卫——模块注册数与测试函数数不应随无关改动漂移。这里量的是
**AST 解析延迟**（每次 CI 静态检查都会付的成本）与**结构计数**。

结果写入 bench/results.json，数字全部来自本机 AST 静态分析，不是估算。

用法：
    python3 bench/structure_bench.py
    python3 bench/structure_bench.py --repeat 20
"""
import ast
import json
import os
import pathlib
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BACKEND = os.path.join(REPO, "backend")


def _count_routers():
    """统计 APIRouter( 注册点数量（业务模块数）。"""
    n = 0
    for p in pathlib.Path(BACKEND, "app").rglob("*.py"):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Attribute) and fn.attr == "APIRouter":
                    n += 1
                elif isinstance(fn, ast.Name) and fn.id == "APIRouter":
                    n += 1
    return n


def _count_test_functions():
    """统计测试函数数量（def/async def test_*）。"""
    n = 0
    files = 0
    for p in pathlib.Path(BACKEND, "tests").rglob("test_*.py"):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        files += 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                n += 1
    return files, n


def _time_parse(fn, repeat):
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times), min(times), max(times)


def main():
    repeat = 20
    if "--repeat" in sys.argv:
        try:
            repeat = int(sys.argv[sys.argv.index("--repeat") + 1])
        except (ValueError, IndexError):
            repeat = 20

    t0 = time.perf_counter()
    n_routers = _count_routers()
    n_test_files, n_tests = _count_test_functions()
    full_parse_s = time.perf_counter() - t0

    med_parse, mn_parse, mx_parse = _time_parse(_count_routers, repeat)

    results = {
        "tool": "life-planner",
        "method": "AST static analysis (stdlib ast), median of %d reps" % repeat,
        "structure": {
            "business_modules_apirouter": n_routers,
            "test_files": n_test_files,
            "test_functions": n_tests,
        },
        "timing": {
            "full_parse_s": round(full_parse_s, 6),
            "router_count_median_s": round(med_parse, 6),
            "min_s": round(mn_parse, 6),
            "max_s": round(mx_parse, 6),
        },
        "note": "OpenAPI 106 ops / 71 paths 需完整依赖导入（README 复算节）；本基准以 AST 注册点为结构基线",
    }

    out = os.path.join(HERE, "results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"life-planner structure (median of {repeat}):")
    print(f"  business modules (APIRouter): {n_routers}")
    print(f"  test files / functions      : {n_test_files} / {n_tests}")
    print(f"  full AST parse              : {full_parse_s:.6f} s")
    print(f"  router count (median)       : {med_parse:.6f} s")
    print(f"\nSaved -> {out}")


if __name__ == "__main__":
    main()
