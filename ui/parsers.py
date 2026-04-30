"""Parsers — CMake target graph, test results, and workspace discovery."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# ─── Workspace discovery ──────────────────────────────────────────────────────

def list_projects() -> list:
    projects_dir = ROOT / "projects"
    if not projects_dir.exists():
        return []
    result = []
    for proj in sorted(projects_dir.iterdir()):
        if not proj.is_dir():
            continue
        modules = [
            mod.name
            for mod in sorted(proj.iterdir())
            if mod.is_dir() and (mod / "CMakeLists.txt").exists()
        ]
        result.append({
            "name": proj.name,
            "modules": modules,
            "path": str(proj.relative_to(ROOT)).replace("\\", "/"),
        })
    return result


def list_build_dirs() -> list:
    result = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        n = d.name
        if n == "build" or n.startswith("build-") or n.startswith("build_"):
            result.append({
                "name": n,
                "configured": (d / "CMakeCache.txt").exists(),
                "path": str(d.relative_to(ROOT)).replace("\\", "/"),
            })
    return result


def list_reports() -> list:
    result = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir():
            continue
        rdir = d / "reports"
        if rdir.exists():
            for f in sorted(rdir.iterdir()):
                if f.is_file():
                    result.append({
                        "name": f.name,
                        "build_dir": d.name,
                        "path": str(f.relative_to(ROOT)).replace("\\", "/"),
                    })
    return result


# ─── Target dependency graph ──────────────────────────────────────────────────

def parse_target_graph() -> dict:
    """Parse CMakeLists.txt files under projects/ and return a target dep graph
    with per-node coupling metrics (Ca, Ce, I) and cycle detection."""
    projects_dir = ROOT / "projects"
    nodes: dict = {}
    raw_edges: list = []

    def extract_vars(text: str) -> dict:
        result = {}
        for m in re.finditer(
            r'(?m)^[ \t]*set\s*\(\s*(\w+)\s+"?([^"\)\n]+?)"?\s*\)', text
        ):
            result[m.group(1)] = m.group(2).strip()
        return result

    def resolve(value, vars_dict: dict) -> str:
        if not value:
            return value
        return re.sub(r'\$\{(\w+)\}', lambda m: vars_dict.get(m.group(1), m.group(0)), value)

    def split_deps(s: str) -> list:
        return [d.strip() for d in re.split(r'[;\s]+', s) if d.strip()] if s else []

    for cmake_file in sorted(projects_dir.rglob("CMakeLists.txt")):
        text = cmake_file.read_text(encoding="utf-8", errors="replace")
        rel = str(cmake_file.relative_to(ROOT)).replace("\\", "/")
        is_test = "/tests/" in rel

        v = extract_vars(text)
        name = resolve(v.get("DIR_TARGET_NAME") or v.get("PKG_TARGET_NAME"), v)
        ttype = resolve(v.get("DIR_TARGET_TYPE"), v)
        prefix = resolve(v.get("DIR_ALIAS_PREFIX"), v)

        if not (name and ttype) or name.startswith("${"):
            continue

        alias = f"{prefix}::{name}" if prefix else None
        ttype_up = ttype.upper()
        nodes[name] = {
            "type": "executable" if ttype_up == "EXECUTABLE" else
                    "interface" if ttype_up == "INTERFACE" else "library",
            "alias": alias,
            "file": rel,
            "is_test": is_test and ttype.upper() == "EXECUTABLE",
        }
        for dep_var, kind in [
            ("DIR_PUBLIC_DEPS", "PUBLIC"),
            ("DIR_PRIVATE_DEPS", "PRIVATE"),
            ("DIR_INTERFACE_DEPS", "INTERFACE"),
        ]:
            raw = resolve(v.get(dep_var), v)
            for dep in split_deps(raw):
                raw_edges.append({"from": name, "to": dep, "kind": kind})

    # Resolve alias → canonical names
    alias_map = {n["alias"]: nid for nid, n in nodes.items() if n["alias"]}
    edges = [
        {"from": e["from"], "to": alias_map.get(e["to"], e["to"]), "kind": e["kind"]}
        for e in raw_edges
    ]

    # Adjacency list
    adj: dict = {}
    for e in edges:
        adj.setdefault(e["from"], [])
        if e["to"] not in adj[e["from"]]:
            adj[e["from"]].append(e["to"])

    def transitive(target: str, seen: set = None) -> set:
        if seen is None:
            seen = set()
        if target in seen:
            return set()
        seen.add(target)
        result = set()
        for dep in adj.get(target, []):
            result.add(dep)
            result |= transitive(dep, seen)
        return result

    # Afferent coupling (Ca)
    ca = {nid: 0 for nid in nodes}
    for e in edges:
        if e["to"] in ca:
            ca[e["to"]] += 1

    # Cycle detection — DFS coloring
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in nodes}
    in_cycle: set = set()

    def dfs_cycle(v: str):
        color[v] = GRAY
        for w in adj.get(v, []):
            if w not in color:
                continue
            if color[w] == GRAY:
                in_cycle.add(v)
                in_cycle.add(w)
            elif color[w] == WHITE:
                dfs_cycle(w)
                if w in in_cycle:
                    in_cycle.add(v)
        color[v] = BLACK

    for nid in nodes:
        if color[nid] == WHITE:
            dfs_cycle(nid)

    # Assemble result
    node_list = []
    for nid, n in nodes.items():
        trans = sorted(transitive(nid))
        ce = len(adj.get(nid, []))
        ca_val = ca[nid]
        total = ca_val + ce
        instability = round(ce / total, 2) if total > 0 else None
        node_list.append({
            "id": nid, **n,
            "transitive_deps": trans,
            "metrics": {
                "ca": ca_val,
                "ce": ce,
                "instability": instability,
                "transitive_count": len(trans),
                "in_cycle": nid in in_cycle,
            },
        })
    return {"nodes": node_list, "edges": edges}


# ─── Test result parsing ──────────────────────────────────────────────────────

def parse_test_results(build_dir: Path):
    """Return parsed test results for a build dir, or None if none exist."""
    junit = build_dir / "reports" / "tests.junit.xml"
    if junit.exists():
        return _parse_junit(junit)
    lastlog = build_dir / "Testing" / "Temporary" / "LastTest.log"
    if lastlog.exists():
        return _parse_lasttest(lastlog)
    return None


def _parse_junit(path: Path) -> dict:
    try:
        root = ET.parse(str(path)).getroot()
        suite = root if root.tag == "testsuite" else (root.find("testsuite") or root)
        total    = int(suite.get("tests", 0))
        failures = int(suite.get("failures", 0))
        errors   = int(suite.get("errors", 0))
        skipped  = int(suite.get("skipped", 0))
        passed   = total - failures - errors - skipped
        tests = []
        for tc in suite.findall("testcase"):
            fail_el = tc.find("failure") or tc.find("error")
            skip_el = tc.find("skipped")
            if fail_el is not None:
                status = "failed"
                message = (fail_el.get("message", "") or (fail_el.text or ""))[:200]
            elif skip_el is not None:
                status = "skipped"
                message = skip_el.get("message", "")
            else:
                status = "passed"
                message = ""
            tests.append({
                "name": tc.get("name", "?"),
                "status": status,
                "time": round(float(tc.get("time", 0)), 3),
                "message": message.strip(),
            })
        return {"total": total, "passed": passed, "failed": failures + errors,
                "skipped": skipped, "tests": tests, "source": "junit"}
    except Exception as e:
        return {"total": 0, "passed": 0, "failed": 0, "skipped": 0,
                "tests": [], "source": "junit", "error": str(e)}


def _parse_lasttest(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    tests = []
    for m in re.finditer(
        r'(?m)^(\d+)/\d+ Test(?:ing)?: (.+?)\n.*?Test (?:Passed|Failed)\.',
        text, re.DOTALL
    ):
        name = m.group(2).strip()
        passed = "Test Passed" in m.group(0)
        time_m = re.search(r'Test time =\s+([\d.]+)', m.group(0))
        tests.append({
            "name": name,
            "status": "passed" if passed else "failed",
            "time": float(time_m.group(1)) if time_m else 0.0,
            "message": "",
        })
    total = len(tests)
    failed = sum(1 for t in tests if t["status"] == "failed")
    return {"total": total, "passed": total - failed, "failed": failed,
            "skipped": 0, "tests": tests, "source": "lasttest"}
