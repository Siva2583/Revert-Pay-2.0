"""Parse-check every equation and inline math fragment before building."""
import importlib
import re
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib.mathtext import MathTextParser
from matplotlib.font_manager import FontProperties

sys.path.insert(0, ".")
from framework import _flat_frac, _shrink_ops

P = MathTextParser("path")
props = FontProperties(size=10)


def check(tex, where, display):
    body = tex.replace(chr(92) + "frac", chr(92) + "dfrac") if display else tex
    try:
        P.parse("$" + body + "$", dpi=72, prop=props)
        return True
    except Exception as e:
        print(f"[FAIL] {where}: {tex[:90]}")
        print("       " + str(e).replace("\n", " ")[:200])
        return False


bad = total = 0
for mod_name in ("content_u3", "content_u4", "content_u5"):
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError:
        continue
    for num, script in mod.SCRIPTS.items():
        where = f"{mod_name} Q{num}"
        for line in script.split("\n"):
            s = line.strip()
            if s.startswith("@@ ") or s.startswith("$$ "):
                total += 1
                if not check(s[3:].strip(), where + " display", True):
                    bad += 1
                continue
            for frag in re.findall(r'\$([^$]+)\$', s):
                total += 1
                if not check(_shrink_ops(_flat_frac(frag)), where + " inline", False):
                    bad += 1
print(f"checked {total} fragments, {bad} failures")
sys.exit(1 if bad else 0)
