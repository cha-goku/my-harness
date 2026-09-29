#!/usr/bin/env python3
"""픽스처 테스트. 정상 입력은 통과해야 하고, 위반 입력은 기대한 규칙에 걸려야 한다.

사용법: python3 check/run_fixtures.py
"""
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check  # noqa: E402

ROOT = HERE.parent
VALID = ROOT / "fixtures" / "valid"
CASES = ROOT / "fixtures" / "cases.json"


def set_path(obj, path, value):
    keys = [int(k) if k.isdigit() else k for k in re.findall(r"[^.\[\]]+", path)]
    for k in keys[:-1]:
        obj = obj[k]
    obj[keys[-1]] = value


def apply(file, op, args):
    text = file.read_text(encoding="utf-8")
    if op == "text_replace":
        if args[0] not in text:
            raise SystemExit(f"픽스처 오류: {file.name}에 {args[0]!r} 없음")
        text = text.replace(args[0], args[1], 1)
    elif op == "text_set":
        text = args[0]
    elif op == "text_append":
        text += args[0]
    elif op == "json_set":
        if file.suffix == ".json":
            data = json.loads(text)
            set_path(data, args[0], args[1])
            text = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            m = re.search(r"```json\s*\n(.*?)\n```", text, re.S)
            data = json.loads(m.group(1))
            set_path(data, args[0], args[1])
            block = json.dumps(data, ensure_ascii=False, indent=2)
            text = text[:m.start(1)] + block + text[m.end(1):]
    else:
        raise SystemExit(f"알 수 없는 op: {op}")
    file.write_text(text, encoding="utf-8")


def main():
    rules = check.load_json(ROOT / "rules.json")
    problems = 0
    total = 0

    for gate in ("g1", "g2", "g3", "s5"):
        total += 1
        r = check.run_check(gate, VALID, rules)
        if not r["passed"]:
            problems += 1
            print(f"FAIL  valid/{gate}: 정상 입력이 통과하지 못함 {r['failures']}")
    shutil.rmtree(VALID / "review", ignore_errors=True)

    for case in json.loads(CASES.read_text(encoding="utf-8")):
        total += 1
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / "run"
            shutil.copytree(VALID, run)
            for o in case.get("ops") or [{"op": case["op"], "args": case["args"]}]:
                apply(run / case["file"], o["op"], o["args"])
            r = check.run_check(case["check"], run, rules)
        ids = {f["rule"] for f in r["failures"]}
        if case["expect"] == "PASS":
            if not r["passed"]:
                problems += 1
                print(f"FAIL  {case['id']}: 통과해야 하는데 실패함 {r['failures']}")
            else:
                print(f"ok    {case['id']}")
        elif case["expect"] not in ids:
            problems += 1
            print(f"FAIL  {case['id']}: 기대 {case['expect']} / 실제 {sorted(ids) or '통과'}")
        elif "FILE" in ids and case["expect"] != "FILE":
            problems += 1
            print(f"FAIL  {case['id']}: 형식 오류로 실패함 {r['failures']}")
        else:
            print(f"ok    {case['id']}")

    print(f"\n{total - problems}/{total} 통과")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
