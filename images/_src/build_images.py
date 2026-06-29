# -*- coding: utf-8 -*-
"""
ML_COMMERCE RFM 시각화 빌드 스크립트
- Graphviz(dot)로 통일된 디자인의 이미지 3종 생성
- 디자인 톤: Indigo + Teal modern
- 분류 로직 출처: eda/final/02_RFM Analysis_CIG.ipynb -> set_customer_category_ver4
"""
import subprocess, sys, os

SRC = os.path.dirname(os.path.abspath(__file__))           # images/_src  (.dot 출력)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(SRC, ".."))  # images/ (.png 출력)
FONT = "Malgun Gothic"

# ---- 디자인 토큰 ----
INDIGO      = "#4F46E5"   # 핵심 그룹(강조)
INDIGO_DK   = "#3730A3"
INDIGO_SUB  = "#C7D2FE"   # 인디고 위 보조 텍스트
TEAL_FILL   = "#CCFBF1"   # 의사결정 노드
TEAL_BORDER = "#14B8A6"
TEAL_DK     = "#0F766E"
TEAL        = "#0D9488"   # YES / 상승(▲)
SLATE_FILL  = "#E2E8F0"   # 비핵심 그룹
SLATE_BD    = "#CBD5E1"
SLATE_TX    = "#334155"
SLATE_SUB   = "#64748B"
SLATE_EDGE  = "#94A3B8"   # NO
ROSE        = "#E11D48"   # 하락(▼)
INK         = "#1E293B"
TINT        = "#EEF2FF"   # 아주 옅은 인디고 배경

def render(dot, name):
    path = os.path.join(SRC, name + ".dot")
    with open(path, "w", encoding="utf-8") as f:
        f.write(dot)
    png = os.path.join(OUT, name + ".png")
    subprocess.run(["dot", "-Tpng", "-Gdpi=200", path, "-o", png], check=True)
    print("rendered", png)

# ============================================================
# 1) Decision Tree (consolidated, ver4 logic)
# ============================================================
# (조건, 세그먼트EN, 한글설명, 핵심여부)
STEPS = [
    ("R&gt;3 &amp; F&gt;3\n&amp; M&gt;3",  "Loyal Champion",          "충성 우수 고객",   True),
    ("R&lt;3 &amp; F≥3\n&amp; M≥3", "Potential Loyalist",   "충성 전환 유망",   True),
    ("R&gt;3 &amp; M≥3",              "Promising Newcomer",      "유망 신규 고객",   True),
    ("F&gt;3 &amp; M≤3",              "Bargain Lover",           "실속형 고객",     True),
    ("R&gt;3",                             "New Customer",            "신규 고객",       False),
    ("M&gt;3",                             "Sleeping Value Customer", "휴면 우량 고객",   False),
    ("R&lt;3 &amp; F&lt;3\n&amp; M&lt;3",  "Need Attention",          "관리 필요 고객",   False),
    ("R&lt;3",                             "Inactive Customer",       "비활성 고객",     False),
    ("F&lt;3",                             "Infrequent Shoppers",     "저빈도 고객",     False),
    ("M&lt;3",                             "Low Spenders",            "소액 구매 고객",   False),
]
ELSE_LEAF = ("Diverse Needs", "기타 다양한 요구", False)

def leaf_node(nid, en, ko, core):
    fill = INDIGO if core else SLATE_FILL
    main = "white" if core else INK
    sub  = INDIGO_SUB if core else SLATE_SUB
    bd   = INDIGO_DK if core else SLATE_BD
    lab = (f'<<FONT POINT-SIZE="13"><B>{en}</B></FONT>'
           f'<BR/><FONT POINT-SIZE="9" COLOR="{sub}">{ko}</FONT>>')
    return (f'  "{nid}" [shape=box, style="rounded,filled", fillcolor="{fill}", '
            f'color="{bd}", penwidth=1.2, fontcolor="{main}", margin="0.16,0.10", label={lab}];\n')

dot = []
dot.append('digraph RFMTree {')
dot.append('  rankdir=TB; bgcolor="white"; splines=polyline;')
dot.append(f'  graph [fontname="{FONT}", ranksep=0.50, nodesep=0.45];')
dot.append(f'  node [fontname="{FONT}"];')
dot.append(f'  edge [fontname="{FONT}", fontsize=10, color="{SLATE_EDGE}", penwidth=1.3, arrowsize=0.7];')
# title
dot.append(f'  title [shape=plaintext, label=<<FONT POINT-SIZE="22" COLOR="{INK}"><B>RFM Decision Tree</B></FONT>'
           f'<BR/><FONT POINT-SIZE="11" COLOR="{SLATE_SUB}">RFM 점수 기반 11개 고객 세그먼트 분류 (핵심 4 · 비핵심 7)</FONT>>];')
# legend
dot.append(f'  legend [shape=plaintext, label=<'
           f'<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="6" CELLPADDING="2">'
           f'<TR><TD BGCOLOR="{INDIGO}" WIDTH="16"></TD><TD><FONT POINT-SIZE="10" COLOR="{INK}">핵심 그룹</FONT></TD>'
           f'<TD WIDTH="12"></TD>'
           f'<TD BGCOLOR="{SLATE_FILL}" WIDTH="16"></TD><TD><FONT POINT-SIZE="10" COLOR="{INK}">비핵심 그룹</FONT></TD></TR>'
           f'</TABLE>>];')

# condition nodes + leaves
for i, (cond, en, ko, core) in enumerate(STEPS, start=1):
    c = f"c{i}"
    L = f"L{i}"
    dot.append(f'  "{c}" [shape=diamond, style=filled, fillcolor="{TEAL_FILL}", color="{TEAL_BORDER}", '
               f'penwidth=1.4, fontcolor="{TEAL_DK}", fontsize=11, label="{cond}"];')
    dot.append(leaf_node(L, en, ko, core).rstrip())
# else leaf
en, ko, core = ELSE_LEAF
dot.append(leaf_node("L11", en, ko, core).rstrip())

# title/legend placement
dot.append('  title -> c1 [style=invis];')
dot.append('  {rank=same; title; legend;}')

# edges
for i in range(1, len(STEPS) + 1):
    c = f"c{i}"
    L = f"L{i}"
    dot.append(f'  "{c}" -> "{L}" [label="YES", color="{TEAL}", fontcolor="{TEAL_DK}"];')
    dot.append(f'  {{rank=same; "{c}"; "{L}";}}')
    if i < len(STEPS):
        dot.append(f'  "{c}" -> "c{i+1}" [label="NO", color="{SLATE_EDGE}", fontcolor="{SLATE_SUB}"];')
    else:
        dot.append(f'  "{c}" -> "L11" [label="else", color="{SLATE_EDGE}", fontcolor="{SLATE_SUB}"];')
dot.append('}')
render("\n".join(dot), "Decision_Tree_RFM")

# ============================================================
# 2) RFM_ANALYSIS : 핵심 그룹별 RFM 시그니처 + 마케팅 전략
# ============================================================
def sig(r, f, m):
    """r,f,m in {'up','down'} -> HTML cells"""
    def arr(v):
        return (f'<FONT COLOR="{TEAL}"><B>▲</B></FONT>' if v == 'up'
                else f'<FONT COLOR="{ROSE}"><B>▼</B></FONT>')
    cells = ""
    for lbl, v in (("R", r), ("F", f), ("M", m)):
        cells += (f'<TD BGCOLOR="{TINT}" CELLPADDING="6">'
                  f'<FONT POINT-SIZE="11" COLOR="{SLATE_TX}"><B>{lbl}</B></FONT> {arr(v)}</TD>')
    return cells

ROWS2 = [
    ("Loyal Champion",      ('up','up','up'),   "우수고객 차별화 서비스 · VVIP 전용 마케팅"),
    ("Potential Loyalist",  ('down','up','up'), "재구매 유도 캠페인 · 구매 주기 검토"),
    ("Promising Newcomer",  ('up','down','up'), "제품 연관성 분석 기반 추천 · 구매확률 높은 상품 제안"),
    ("Bargain Lover",       ('up','up','down'), "구매 금액 증대 마케팅 · 고가 제품 구매 혜택"),
]
t = []
t.append('digraph Analysis {')
t.append('  bgcolor="white"; node [shape=plaintext];')
t.append(f'  graph [fontname="{FONT}"];  node [fontname="{FONT}"];')
rows = ""
for en, (r,f,m), strat in ROWS2:
    rows += (
        '<TR>'
        f'<TD BGCOLOR="{INDIGO}" CELLPADDING="12" ALIGN="LEFT" WIDTH="190">'
        f'<FONT POINT-SIZE="13" COLOR="white"><B>{en}</B></FONT></TD>'
        f'{sig(r,f,m)}'
        f'<TD BGCOLOR="white" CELLPADDING="12" ALIGN="LEFT" WIDTH="430">'
        f'<FONT POINT-SIZE="11" COLOR="{INK}">{strat}</FONT></TD>'
        '</TR>'
        f'<TR><TD COLSPAN="5" HEIGHT="6"></TD></TR>'
    )
t.append('  tbl [label=<'
         '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'
         f'<TR><TD COLSPAN="5" ALIGN="LEFT" CELLPADDING="8">'
         f'<FONT POINT-SIZE="20" COLOR="{INK}"><B>RFM 핵심 그룹별 마케팅 전략</B></FONT></TD></TR>'
         f'<TR><TD COLSPAN="5" HEIGHT="10"></TD></TR>'
         f'{rows}'
         '</TABLE>>];')
t.append('}')
render("\n".join(t), "RFM_ANALYSIS")

# ============================================================
# 3) RFM_CUSTOMER : 핵심 4그룹 x R/F/M 시그니처 표
# ============================================================
SEGS = ["Loyal Champions", "Potential Loyalist", "Promising Newcomers", "Bargain Lovers"]
MAT = {
    "Recency":        ['up','down','up','up'],
    "Frequency":      ['up','up','down','up'],
    "Monetary Value": ['up','up','up','down'],
}
def arrow(v):
    return (f'<FONT POINT-SIZE="22" COLOR="{TEAL}"><B>▲</B></FONT>' if v=='up'
            else f'<FONT POINT-SIZE="22" COLOR="{ROSE}"><B>▼</B></FONT>')

c = []
c.append('digraph Customer {')
c.append('  bgcolor="white"; node [shape=plaintext];')
c.append(f'  graph [fontname="{FONT}"];  node [fontname="{FONT}"];')
# header
header = (f'<TD BGCOLOR="white" WIDTH="150"></TD>')
for s in SEGS:
    header += (f'<TD BGCOLOR="{INDIGO}" CELLPADDING="12" WIDTH="160">'
               f'<FONT POINT-SIZE="12" COLOR="white"><B>{s}</B></FONT></TD>')
body = ""
for metric, vals in MAT.items():
    body += f'<TR><TD BGCOLOR="{INDIGO_DK}" CELLPADDING="12" ALIGN="LEFT"><FONT POINT-SIZE="12" COLOR="white"><B>{metric}</B></FONT></TD>'
    for v in vals:
        body += f'<TD BGCOLOR="{TINT}" CELLPADDING="14">{arrow(v)}</TD>'
    body += '</TR>'
c.append('  tbl [label=<'
         '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="6" CELLPADDING="0">'
         f'<TR><TD COLSPAN="5" ALIGN="LEFT" CELLPADDING="8">'
         f'<FONT POINT-SIZE="20" COLOR="{INK}"><B>RFM에 따른 핵심 고객 분류</B></FONT></TD></TR>'
         f'<TR><TD COLSPAN="5" HEIGHT="8"></TD></TR>'
         f'<TR>{header}</TR>'
         f'{body}'
         '</TABLE>>];')
c.append('}')
render("\n".join(c), "RFM_CUSTOMER")

print("DONE")
