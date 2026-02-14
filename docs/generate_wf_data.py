#!/usr/bin/env python3
"""Generate wf-data.js from workflow markdown sources."""
import json, re, os, yaml

WF_DIR = os.path.expanduser("~/oikos/hegemonikon/.agent/workflows")

def parse_frontmatter(path):
    """Extract YAML frontmatter from markdown file."""
    with open(path, 'r') as f:
        content = f.read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not m:
        return {}, content
    try:
        fm = yaml.safe_load(m.group(1))
    except:
        fm = {}
    return fm or {}, m.group(2)

def extract_phases(body, fm):
    """Extract detailed phase descriptions from body text."""
    phases = []
    # Look for PHASE/STEP/Ph patterns
    for m in re.finditer(r'(?:^|\n)#+\s*((?:PHASE|STEP|Ph)\s*[\d.]+[^:\n]*)[:\s]*([^\n]*(?:\n(?!#)[^\n]*){0,5})', body):
        title = m.group(1).strip()
        desc = m.group(2).strip()
        # Clean up desc - take first meaningful sentence
        desc_lines = [l.strip() for l in desc.split('\n') if l.strip() and not l.strip().startswith('|') and not l.strip().startswith('>') and not l.strip().startswith('```')]
        desc_clean = ' '.join(desc_lines[:3])
        if desc_clean:
            phases.append(f"{title}: {desc_clean[:200]}")
        else:
            phases.append(title)
    
    # Also try bullet-style phases
    if not phases:
        for m in re.finditer(r'\d+\.\s+\*\*([^*]+)\*\*[:\s]*([^\n]+)', body):
            phases.append(f"{m.group(1).strip()}: {m.group(2).strip()[:150]}")
    
    return phases if phases else ["(詳細はSKILL.md参照)"]

def extract_derivatives(fm, body):
    """Extract derivative modes with descriptions."""
    derivs = []
    raw = fm.get('derivatives', [])
    if not raw:
        return derivs
    
    # Try to find derivative descriptions in body
    for d in raw:
        dname = d if isinstance(d, str) else str(d)
        # Search for --mode=X or ###.*X patterns
        pattern = rf'(?:--mode=|###\s+.*?){re.escape(dname)}[^|]*?\n.*?\*\*目的\*\*[:\s]*([^\n]+)'
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            derivs.append({"name": dname, "desc": m.group(1).strip()[:150]})
        else:
            # Try simpler pattern - look for description after derivative name
            pattern2 = rf'\|\s*\*\*{re.escape(dname)}\*\*\s*\|[^|]*\|([^|]+)\|'
            m2 = re.search(pattern2, body)
            if m2:
                derivs.append({"name": dname, "desc": m2.group(1).strip()[:150]})
            else:
                # Try table format: | name | ccl | description |
                pattern3 = rf'\|\s*{re.escape(dname)}\s*\|[^|]*\|([^|]+)'
                m3 = re.search(pattern3, body)
                if m3:
                    derivs.append({"name": dname, "desc": m3.group(1).strip()[:150]})
                else:
                    derivs.append({"name": dname, "desc": ""})
    return derivs

def extract_usecases(body):
    """Extract use cases from body text."""
    ucs = []
    # Pattern: 使用例, ユースケース, 例:
    for m in re.finditer(r'\*\*例\d*\*\*[:\s]*`?([^`\n]+)`?\s*→\s*([^\n]+)', body):
        ucs.append(f"{m.group(1).strip()} → {m.group(2).strip()[:150]}")
    
    # Pattern: trigger table rows
    for m in re.finditer(r'\|\s*[「`/]([^|]+)\s*\|\s*([^|]+暗黙[^|]*)\s*\|', body):
        ucs.append(f"「{m.group(1).strip()}」 → {m.group(2).strip()[:100]}")
    
    # Pattern: bullet use cases
    for m in re.finditer(r'[-•]\s*([^:\n]+を(?:したい|する|開始|必要|判断|確認)[^\n]*)', body):
        ucs.append(m.group(1).strip()[:150])
    
    return ucs

def build_wf_entry(cmd, fm, body):
    """Build a complete WF data entry."""
    ct = fm.get('category_theory', {})
    adj_label = ct.get('adjunction', '')
    if isinstance(adj_label, dict):
        adj_label = str(adj_label)
    core = ct.get('core', '')
    if isinstance(core, dict):
        core = str(core)
    adj_role = 'F' if 'F⊣' in core or '左随伴' in core else 'G'
    
    tri = fm.get('trigonon', {})
    ca = fm.get('cognitive_algebra', {})
    sel = fm.get('sel_enforcement', {})
    
    # Determine adjunction pair
    pair = ''
    if adj_label:
        m = re.search(r'(\w+)\s*\(F\)\s*⊣\s*(\w+)\s*\(G\)', adj_label)
        if m:
            f_name = m.group(1).lower()[:3]
            g_name = m.group(2).lower()[:3]
            pair = g_name if adj_role == 'F' else f_name
    
    phases = extract_phases(body, fm)
    derivs = extract_derivatives(fm, body)
    usecases = extract_usecases(body)
    
    # Extract detailed derivative info from mode sections
    for d in derivs:
        if not d['desc']:
            # Try to find in body
            pattern = rf'mode={re.escape(d["name"])}[^)]*\).*?\n\n.*?\*\*目的\*\*[:\s]*([^\n]+)'
            m = re.search(pattern, body)
            if m:
                d['desc'] = m.group(1).strip()[:150]
    
    entry = {
        "name": fm.get('name', cmd),
        "jp": fm.get('description', '').split('—')[0].strip() if '—' in fm.get('description', '') else fm.get('description', ''),
        "series": tri.get('series', ''),
        "pos": tri.get('type', '') + str(tri.get('theorem', '')).replace(tri.get('series', ''), 'T') if tri.get('theorem') else '',
        "ver": fm.get('version', ''),
        "desc": fm.get('description', ''),
        "adj": {
            "pair": pair,
            "role": adj_role,
            "label": adj_label,
            "meaning": ct.get('role', '') or ct.get('meaning', ''),
            "f_def": ct.get('F_definition', ct.get('role', '')),
            "g_def": ct.get('G_definition', ''),
        },
        "phases": phases,
        "derivatives": derivs,
        "algebra": {
            "+": ca.get('+', ''),
            "-": ca.get('-', ''),
            "*": ca.get('*', ''),
        },
        "usecases": usecases,
    }
    
    # Add SEL enforcement details
    if sel:
        for k in ['+', '-', '*']:
            if k in sel and isinstance(sel[k], dict):
                reqs = sel[k].get('minimum_requirements', [])
                if reqs and entry['algebra'].get(k):
                    entry['algebra'][k] += ' [必須: ' + ', '.join(reqs[:3]) + ']'
    
    # Fix pos format
    if entry['pos'] and not entry['pos'].startswith('T'):
        # e.g. "PureT1" -> "T1"
        m = re.search(r'T(\d)', entry['pos'])
        if m:
            entry['pos'] = 'T' + m.group(1)
    
    # Natural transformation and duality
    nt = fm.get('natural_transformation', {})
    dual = fm.get('duality', {})
    if nt:
        entry['nat_transform'] = {
            'partner': nt.get('partner', ''),
            'axis': nt.get('shared_axis', ''),
            'meaning': nt.get('meaning', ''),
        }
    if dual:
        entry['duality'] = {
            'partner': dual.get('partner', ''),
            'meaning': dual.get('meaning', ''),
        }
    
    return entry

# Process all 24 theorem WFs
THEOREM_WFS = ['noe','bou','zet','ene','met','mek','sta','pra',
               'pro','pis','ore','dox','kho','hod','tro','tek',
               'euk','chr','tel','sop','pat','dia','gno','epi']

TAU_WFS = ['boot','bye','eat','u','m','vet','dendron','dev']
CCL_WFS = [f for f in os.listdir(WF_DIR) if f.startswith('ccl-') and f.endswith('.md')]

wf_data = {}
for cmd in THEOREM_WFS:
    path = os.path.join(WF_DIR, f"{cmd}.md")
    if os.path.exists(path):
        fm, body = parse_frontmatter(path)
        wf_data[cmd] = build_wf_entry(cmd, fm, body)

tau_data = {}
for cmd in TAU_WFS:
    path = os.path.join(WF_DIR, f"{cmd}.md")
    if os.path.exists(path):
        fm, body = parse_frontmatter(path)
        entry = {
            "name": fm.get('name', cmd),
            "jp": fm.get('description', ''),
            "desc": fm.get('description', ''),
            "phases": extract_phases(body, fm),
        }
        ct = fm.get('category_theory', {})
        if ct:
            entry['adj'] = {
                'label': ct.get('adjunction', ''),
                'pair': '',
                'role': 'F' if '左随伴' in ct.get('core', '') else 'G',
            }
        tau_data[cmd] = entry

ccl_data = {}
for fname in sorted(CCL_WFS):
    cmd = fname.replace('.md', '')
    path = os.path.join(WF_DIR, fname)
    fm, body = parse_frontmatter(path)
    ccl_expr = fm.get('ccl_expression', '')
    if isinstance(ccl_expr, dict):
        ccl_expr = str(ccl_expr)
    ccl_data[cmd] = {
        "jp": fm.get('description', '').split('—')[0].strip() if '—' in fm.get('description','') else fm.get('description',''),
        "ccl": ccl_expr,
        "desc": fm.get('description', ''),
        "phases": extract_phases(body, fm),
        "usecases": extract_usecases(body),
    }

# Write output
output = {
    "WF_DATA": wf_data,
    "TAU_DATA": tau_data,
    "CCL_DATA": ccl_data,
}

# Write as JS module
with open(os.path.join(os.path.dirname(__file__), 'wf-data.js'), 'w') as f:
    f.write("// Hegemonikón WF Data - Auto-generated\n")
    f.write(f"// Generated from {len(wf_data)} theorem WFs + {len(tau_data)} tau WFs + {len(ccl_data)} CCL macros\n\n")
    
    f.write("const WF_DATA = ")
    json.dump(wf_data, f, ensure_ascii=False, indent=1)
    f.write(";\n\n")
    
    f.write("const TAU_DATA = ")
    json.dump(tau_data, f, ensure_ascii=False, indent=1)
    f.write(";\n\n")
    
    f.write("const CCL_DATA = ")
    json.dump(ccl_data, f, ensure_ascii=False, indent=1)
    f.write(";\n\n")
    
    # Static data
    f.write("""const OMEGA_DATA = {
 o:{name:"O-series Peras",desc:"L1×L1の極限演算で純粋認知の統合判断を生成",targets:["noe","bou","zet","ene"]},
 s:{name:"S-series Peras",desc:"L1×L1.5の極限演算で戦略設計の統合判断を生成",targets:["met","mek","sta","pra"]},
 h:{name:"H-series Peras",desc:"L1×L1.75の極限演算で動機の統合判断を生成",targets:["pro","pis","ore","dox"]},
 p:{name:"P-series Peras",desc:"L1.5×L1.5の極限演算で環境配置の統合判断を生成",targets:["kho","hod","tro","tek"]},
 k:{name:"K-series Peras",desc:"L1.5×L1.75の極限演算で文脈判断の統合を生成",targets:["euk","chr","tel","sop"]},
 a:{name:"A-series Peras",desc:"L1.75×L1.75の極限演算で精度保証の統合判断を生成",targets:["pat","dia","gno","epi"]},
 ax:{name:"Peras の Peras",desc:"6 Series極限を多層的に収束させX-series関係で接続する全体分析",targets:["o","s","h","p","k","a"]},
 x:{name:"X-series 関係層",desc:"定理間の従属関係を可視化・活用する",targets:[]}
};

const X_SERIES = [
 {from:"O",to:"S",shared:"Flow",pairs:"noe↔met, bou↔mek, zet↔sta, ene↔pra"},
 {from:"O",to:"H",shared:"Flow",pairs:"noe↔pro, bou↔pis, zet↔ore, ene↔dox"},
 {from:"S",to:"H",shared:"Flow",pairs:"met↔pro, mek↔pis, sta↔ore, pra↔dox"},
 {from:"S",to:"P",shared:"Scale",pairs:"met↔kho, mek↔hod, sta↔tro, pra↔tek"},
 {from:"S",to:"K",shared:"Scale",pairs:"met↔euk, mek↔chr, sta↔tel, pra↔sop"},
 {from:"P",to:"K",shared:"Scale",pairs:"kho↔euk, hod↔chr, tro↔tel, tek↔sop"},
 {from:"H",to:"A",shared:"Valence",pairs:"pro↔pat, pis↔dia, ore↔gno, dox↔epi"},
 {from:"H",to:"K",shared:"Valence",pairs:"pro↔euk, pis↔chr, ore↔tel, dox↔sop"},
 {from:"K",to:"A",shared:"Valence",pairs:"euk↔pat, chr↔dia, tel↔gno, sop↔epi"}
];

const SERIES_META = {
 O:{name:"Ousia",jp:"本質",color:"#3fb950",bg:"#1a3a2a",level:"L0",gen:"L1×L1"},
 S:{name:"Schema",jp:"様態",color:"#58a6ff",bg:"#1a2a3a",level:"L1",gen:"L1×L1.5"},
 H:{name:"Hormē",jp:"傾向",color:"#f0883e",bg:"#3a2a1a",level:"L2a",gen:"L1×L1.75"},
 P:{name:"Perigraphē",jp:"条件",color:"#d2a8ff",bg:"#2a1a3a",level:"L2b",gen:"L1.5×L1.5"},
 K:{name:"Kairos",jp:"文脈",color:"#f97583",bg:"#3a1a2a",level:"L3",gen:"L1.5×L1.75"},
 A:{name:"Akribeia",jp:"精密",color:"#e6edf3",bg:"#2a2a2a",level:"L4",gen:"L1.75×L1.75"}
};
""")

print(f"Generated wf-data.js:")
print(f"  Theorem WFs: {len(wf_data)}")
for cmd, d in wf_data.items():
    print(f"    /{cmd}: {len(d['phases'])} phases, {len(d['derivatives'])} derivatives, {len(d['usecases'])} usecases")
print(f"  Tau WFs: {len(tau_data)}")
print(f"  CCL Macros: {len(ccl_data)}")
