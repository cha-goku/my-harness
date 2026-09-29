#!/usr/bin/env python3
"""하네스 판정 스크립트. 규칙 값은 rules.json만 읽는다.

사용법:
  check.py g1|g2|g3|s5 --run harness/runs/<묶음>
  check.py docs-sync [--design ../design.md]
결과는 JSON으로 출력하고, 통과하면 종료 코드 0, 아니면 1.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RULES = HERE.parent / "rules.json"
DEFAULT_DESIGN = HERE.parent.parent / "design.md"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read(path):
    return Path(path).read_text(encoding="utf-8")


def norm_color(v):
    if not isinstance(v, str):
        return v
    s = v.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3})", s)
    if m:
        s = "#" + "".join(c * 2 for c in m.group(1))
    return s


def fenced_json(text):
    m = re.search(r"```json\s*\n(.*?)\n```", text, re.S)
    if not m:
        raise ValueError("json 코드 블록이 없다")
    return json.loads(m.group(1))


def fail(rule, detail):
    return {"rule": rule, "detail": detail}


# ---------------------------------------------------------------- 서비스 규칙

def service_checks(screens, rules):
    svc = rules["service"]
    out = []
    for s in screens:
        label = f'{s.get("screen", "?")}/{s.get("variant", "-")}'
        kind = s.get("kind")
        vis = s.get("visibility") or {}
        if kind == "asset_form" and vis.get("default") != svc["default_visibility"]:
            out.append(fail("SVC-1", f'{label}: 공개 범위 기본값이 "{vis.get("default")}" (기대: {svc["default_visibility"]})'))
        if svc["sale_option"] in (vis.get("options") or []):
            roles = set(s.get("roles") or [])
            if not roles or not roles <= set(svc["sale_roles"]):
                out.append(fail("SVC-2", f'{label}: 판매 신청 옵션이 판매 승인 회원 전용이 아님 (roles={sorted(roles)})'))
        for t in s.get("transitions") or []:
            if t.get("to") == svc["approved_status"] and t.get("via_review") is not True:
                out.append(fail("SVC-3", f'{label}: 검수 없이 승인됨으로 가는 전환 {t}'))
        if kind == "admin_review":
            items = s.get("review_checklist") or []
            for c in svc["checklist"]:
                if not any(c["keyword"] in i for i in items):
                    out.append(fail("SVC-4", f'{label}: 체크리스트 항목 없음 "{c["text"]}"'))
            if s.get("approve_enabled_before_checklist_complete") is not False:
                out.append(fail("SVC-5", f"{label}: 체크리스트 완료 전 승인 버튼이 비활성이 아님"))
    return out


# ---------------------------------------------------------------- 프레임 검사 (Figma에서 읽은 값)

def owned_texts(node, nodes):
    """컴포넌트 인스턴스 안의 텍스트를 노드 순서대로 돌려준다. 자식 id는 'I<부모 id>;...' 형태다."""
    base = str(node["id"])
    if not base.startswith("I"):
        base = "I" + base
    prefix = base + ";"
    return [n.get("text", "") for n in nodes
            if n.get("kind") == "text" and str(n.get("id", "")).startswith(prefix)]


def first_text(node, nodes):
    texts = owned_texts(node, nodes)
    return texts[0] if texts else ""


def frame_service_checks(data, rules):
    """서비스 규칙이 Figma 프레임에도 지켜졌는지 본다. 노드의 `text`와 `variant`(컴포넌트 변형 속성)를 읽는다."""
    fc = rules["frame_checks"]
    svc = rules["service"]
    specs = data.get("screens", [])
    frames = data.get("frames", [])
    out = []
    seen_specs = set()
    admin_ok = False

    for fr in frames:
        nodes = fr.get("nodes", [])
        label = fr.get("name") or fr.get("screen")
        spec = next((s for s in specs
                     if s.get("screen") == fr.get("screen") and s.get("variant") == fr.get("variant")), None)
        if spec is None:
            out.append(fail("FRM-0", f'{label}: 설계 문서에 대응하는 화면이 없음 (screen={fr.get("screen")}, variant={fr.get("variant")})'))
            continue
        seen_specs.add((spec.get("screen"), spec.get("variant")))
        kind = spec.get("kind")
        radios = [n for n in nodes if n.get("component") == fc["radio_component"]]
        rows = [n for n in nodes if n.get("component") == fc["checklist_component"]]

        if kind == "asset_form":
            if not radios:
                out.append(fail("FRM-0", f"{label}: 공개 범위 라디오 옵션이 프레임에 없음"))
            selected = [r for r in radios if (r.get("variant") or {}).get("State") == fc["selected_state"]]
            if radios and (len(selected) != 1 or first_text(selected[0], nodes) != fc["default_option_label"]):
                names = [first_text(r, nodes) for r in selected]
                out.append(fail("FRM-1", f'{label}: 기본 선택된 공개 범위가 {names} (기대: ["{fc["default_option_label"]}"] 1개)'))
            only_seller = bool(spec.get("roles")) and set(spec["roles"]) <= set(svc["sale_roles"])
            for r in radios:
                if first_text(r, nodes) == fc["sale_option_label"] and not only_seller:
                    out.append(fail("FRM-2", f'{label}: "{fc["sale_option_label"]}" 옵션이 판매 승인 회원 전용 화면이 아님 (roles={spec.get("roles")})'))

        if kind == "admin_review" and rows:
            admin_ok = True
            items = [r for r in rows if (r.get("variant") or {}).get("Kind") in fc["checklist_item_kinds"]]
            texts = [" ".join(owned_texts(r, nodes)) for r in items]
            if len(items) != len(svc["checklist"]):
                out.append(fail("FRM-4", f'{label}: 체크리스트 항목 행 {len(items)}개 (기대: {len(svc["checklist"])}개)'))
            for c in svc["checklist"]:
                if not any(c["keyword"] in t for t in texts):
                    out.append(fail("FRM-4", f'{label}: 체크리스트 행에 "{c["text"]}" 없음'))
            unchecked = [r for r in rows if (r.get("variant") or {}).get("State") != fc["checked_state"]]
            approves = [n for n in nodes if n.get("kind") == "button" and first_text(n, nodes) == fc["approve_label"]]
            if not approves:
                out.append(fail("FRM-3", f'{label}: "{fc["approve_label"]}" 버튼이 프레임에 없음'))
            elif unchecked:
                for b in approves:
                    if b.get("component") != fc["disabled_component"]:
                        out.append(fail("FRM-3", f'{label}: 체크 안 된 행 {len(unchecked)}개가 있는데 승인 버튼이 비활성이 아님 (component={b.get("component")})'))

    for s in specs:
        key = (s.get("screen"), s.get("variant"))
        if s.get("kind") == "asset_form" and key not in seen_specs:
            out.append(fail("FRM-0", f'설계 화면 "{key[0]}/{key[1]}"에 대응하는 프레임이 없음'))
    if any(s.get("kind") == "admin_review" for s in specs) and not admin_ok:
        out.append(fail("FRM-3", "체크리스트 행이 있는 운영자 검수 프레임이 없음"))
    return out


# ---------------------------------------------------------------- 게이트

def check_g1(run, rules):
    g = rules["g1"]
    out = []
    ref = read(run / "research/01-references.md")
    ana = read(run / "research/02-analysis.md")
    refs = re.findall(r"^- \[(R\d+)\](.*)$", ref, re.M)
    if len(refs) < g["min_references"]:
        out.append(fail("G1-1", f'레퍼런스 {len(refs)}개 (기대: {g["min_references"]}개 이상)'))
    for rid, body in refs:
        if not re.search(r"https?://\S*" + re.escape(g["reference_url_contains"]) + r"\S*", body):
            out.append(fail("G1-2", f"{rid}: uibowl 링크 없음"))
    ids = {rid for rid, _ in refs}
    refl = re.findall(r"^- \[(A\d+)\](.*)$", ana, re.M)
    if len(refl) < g["min_reflections"]:
        out.append(fail("G1-3", f'반영할 부분 {len(refl)}개 (기대: {g["min_reflections"]}개 이상)'))
    for aid, body in refl:
        m = re.search(r"근거:\s*(R\d+(?:\s*,\s*R\d+)*)", body)
        cited = re.findall(r"R\d+", m.group(1)) if m else []
        if not cited or any(c not in ids for c in cited):
            out.append(fail("G1-4", f"{aid}: 근거 레퍼런스 번호가 없거나 존재하지 않음"))
    return out


def check_g2(run, rules):
    g = rules["g2"]
    out = []
    text = read(run / "spec/03-screen-spec.md")
    screens = fenced_json(text)["screens"]
    state = load_json(run / "state.json")
    have = {s.get("screen") for s in screens}
    for name in state.get("screens", []):
        if name not in have:
            out.append(fail("G2-1", f'설계 문서에 화면 없음: "{name}"'))
    for s in screens:
        roles = s.get("roles") or []
        if not roles or any(r not in g["roles"] for r in roles):
            out.append(fail("G2-2", f'{s.get("screen")}: 역할이 PRD §7 범위 밖이거나 비어 있음 {roles}'))
    scrubbed = text
    for phrase in g["excluded_terms_allowlist"]:
        scrubbed = scrubbed.replace(phrase, "")
    for term in g["mvp_excluded_terms"]:
        n = scrubbed.count(term)
        if n:
            out.append(fail("G2-3", f'MVP 제외 단어 "{term}" {n}회'))
    out.extend(service_checks(screens, rules))
    return out


def check_g3(run, rules):
    g = rules["g3"]
    fr = rules["tokens"]["frame"]
    out = []
    frames = fenced_json(read(run / "concept/04-keyscreens.md"))["frames"]
    if not g["min_keyscreens"] <= len(frames) <= g["max_keyscreens"]:
        out.append(fail("G3-1", f'키스크린 {len(frames)}개 (기대: {g["min_keyscreens"]}~{g["max_keyscreens"]}개)'))
    for f in frames:
        if f.get("width") != fr["width"] or f.get("height") != fr["height"]:
            out.append(fail("G3-2", f'{f.get("name")}: {f.get("width")}×{f.get("height")} (기대: {fr["width"]}×{fr["height"]})'))
    state = load_json(run / "state.json")
    if state.get("g3_approved") is not True:
        out.append(fail("G3-3", "사람 컨펌 대기 (state.json의 g3_approved가 true가 아님)"))
    return out


def check_s5(run, rules):
    t = rules["tokens"]
    dr = rules["design_rules"]
    data = load_json(run / "build/design-export.json")
    palette = {norm_color(v) for v in t["colors"].values()} | {norm_color(v) for v in t["extra_colors"]}
    out = []
    for frame in data.get("frames", []):
        fname = frame.get("screen", "?")
        sp = frame.get("side_padding") or {}
        if sp.get("left") != t["frame"]["side_padding"] or sp.get("right") != t["frame"]["side_padding"]:
            out.append(fail("D-8", f"{fname}: 좌우 여백 {sp} (기대: {t['frame']['side_padding']})"))
        accent_nodes = 0
        for n in frame.get("nodes", []):
            nid = f'{fname}/{n.get("id", "?")}'
            kind = n.get("kind")
            w = n.get("font_weight")
            if w is not None and w not in t["font_weights"]:
                out.append(fail("D-1", f"{nid}: 폰트 굵기 {w}"))
            if kind == "app-icon":
                ratio = n.get("radius_ratio")
                if ratio is None or abs(ratio - t["app_icon_radius_ratio"]) > t["app_icon_radius_tolerance"]:
                    out.append(fail("D-2", f"{nid}: 앱 아이콘 모서리 비율 {ratio}"))
            elif n.get("radius") is not None and n["radius"] not in t["radius"]:
                out.append(fail("D-2", f'{nid}: 모서리 {n["radius"]}px'))
            if (n.get("shadows") or 0) > 0 and n.get("component") not in dr["shadow_exceptions"]:
                out.append(fail("D-3", f"{nid}: 그림자 {n['shadows']}개"))
            if kind in dr["pill_kinds"] and n.get("radius") != dr["pill_radius"]:
                out.append(fail("D-4", f'{nid}: {kind} 모서리 {n.get("radius")} (기대: {dr["pill_radius"]})'))
            ls = n.get("letter_spacing")
            if ls is not None and ls != dr["letter_spacing"]:
                out.append(fail("D-5", f"{nid}: 글자 간격 {ls}"))
            if kind != "image":
                for key in ("fill", "stroke", "text_color"):
                    v = n.get(key)
                    if v is not None and norm_color(v) not in palette:
                        out.append(fail("D-6", f"{nid}: {key} {v} 는 팔레트 밖"))
            colors = [norm_color(n.get(k)) for k in ("fill", "stroke", "text_color")]
            accent = norm_color(t["colors"]["accent"])
            if accent in colors:
                accent_nodes += 1
            if kind in dr["accent"]["forbidden_fill_kinds"] and norm_color(n.get("fill")) == accent:
                out.append(fail("D-7", f"{nid}: {kind} 채움에 accent 사용"))
            values = list(n.get("padding") or [])
            if n.get("gap") is not None:
                values.append(n["gap"])
            for v in values:
                if v % t["spacing_step"] != 0:
                    out.append(fail("D-8", f"{nid}: 간격 {v} 는 {t['spacing_step']}의 배수가 아님"))
        if accent_nodes > dr["accent"]["max_per_frame"]:
            out.append(fail("D-7", f'{fname}: accent 사용 {accent_nodes}곳 (기대: {dr["accent"]["max_per_frame"]}곳 이하)'))
    out.extend(service_checks(data.get("screens", []), rules))
    out.extend(frame_service_checks(data, rules))
    return out


# ---------------------------------------------------------------- 문서 간 일치

def check_docs_sync(design_path, rules):
    text = read(design_path)
    t = rules["tokens"]
    out, notes = [], []
    doc_colors = dict(re.findall(r"\{colors\.([a-z-]+)\}`\s*—\s*(#[0-9a-fA-F]{6})", text))
    for k, v in doc_colors.items():
        if k not in t["colors"]:
            out.append(fail("DOC-1", f"색 {k}: design.md에만 있음"))
        elif norm_color(v) != norm_color(t["colors"][k]):
            out.append(fail("DOC-1", f"색 {k}: design.md {v} / rules.json {t['colors'][k]}"))
    for k in t["colors"]:
        if k not in doc_colors:
            notes.append(f"색 {k}: rules.json에만 있음 (design.md에 값 없음)")
    doc_radius = {int(v) for v in re.findall(r"\{rounded\.\w+\}`\s*\|\s*(\d+)px", text)}
    if doc_radius != set(t["radius"]):
        out.append(fail("DOC-2", f"모서리: design.md {sorted(doc_radius)} / rules.json {sorted(t['radius'])}"))
    doc_spacing = {int(v) for v in re.findall(r"\{spacing\.[\w-]+\}`\s*(\d+)px", text)}
    if doc_spacing != set(t["spacing_values"]):
        out.append(fail("DOC-3", f"간격: design.md {sorted(doc_spacing)} / rules.json {sorted(t['spacing_values'])}"))
    doc_weights = {int(v) for v in re.findall(r"\{typography\.[\w-]+\}`\s*\|\s*\d+px\s*\|\s*(\d+)", text)}
    if doc_weights != set(t["font_weights"]):
        out.append(fail("DOC-4", f"굵기: design.md {sorted(doc_weights)} / rules.json {sorted(t['font_weights'])}"))
    m = re.search(r"Baseline\s*\|\s*(\d+)\s*×\s*(\d+)", text)
    if not m or (int(m.group(1)), int(m.group(2))) != (t["frame"]["width"], t["frame"]["height"]):
        out.append(fail("DOC-5", f"프레임 크기: design.md {m.groups() if m else None} / rules.json {t['frame']['width']}×{t['frame']['height']}"))
    return out, notes


# ---------------------------------------------------------------- 실행

CHECKS = {"g1": check_g1, "g2": check_g2, "g3": check_g3, "s5": check_s5}


def run_check(cmd, run, rules):
    """cmd 검사를 실행해 결과 dict를 돌려준다. 파일이 없거나 형식이 틀리면 FILE 실패로 처리한다."""
    try:
        failures = CHECKS[cmd](Path(run), rules)
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError) as e:
        failures = [fail("FILE", f"{type(e).__name__}: {e}")]
    return {"check": cmd, "passed": not failures, "failure_count": len(failures), "failures": failures}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=[*CHECKS, "docs-sync"])
    ap.add_argument("--run")
    ap.add_argument("--rules", default=str(DEFAULT_RULES))
    ap.add_argument("--design", default=str(DEFAULT_DESIGN))
    a = ap.parse_args()
    rules = load_json(a.rules)
    if a.cmd == "docs-sync":
        failures, notes = check_docs_sync(a.design, rules)
        result = {"check": "docs-sync", "passed": not failures, "failure_count": len(failures), "failures": failures, "notes": notes}
    else:
        if not a.run:
            ap.error("--run 이 필요하다")
        result = run_check(a.cmd, a.run, rules)
        if a.cmd == "s5":
            review = Path(a.run) / "review"
            review.mkdir(parents=True, exist_ok=True)
            (review / "06-review.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
