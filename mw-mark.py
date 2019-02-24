#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools, argparse
import shared

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignment", required=True, help="word alignment")
    parser.add_argument("--tree", required=True, help="parse tree")
    args = parser.parse_args()                                
    for align, s in itertools.izip(open(args.alignment), open(args.tree)):
        align = unicode(align).rstrip()
        if align == "": print; continue # sanity check
        align = [map(int, x.split("-")) for x in align.split(" ")]
        s = unicode(s).rstrip()
        if s == "": print; continue # sanity check
        s = shared.parse(shared.tokenize(s))
        marked, after = mark(s, align)
        print shared.pritty(marked)

def mark(node, align, root=True):
    r = []; j = []; global count
    if root: count = 0
    for no, child in enumerate(node):
        if not isinstance(child, list):
            if no != 0:
                jjj = []
                for f, e in align:
                    if f == count: jjj.append(e)
                count += 1; j.append(shared.median(jjj))
            r.append(child); continue
        rr, jj = mark(child, align, False)
        r.append(rr); j.append(jj)
    if r != [] and len(node) >= 3:
        first = shared.flatten(j[0]); second = shared.flatten(j[1])
        t = shared.tau(first + second) - shared.tau(second + first)
        r[0] = "%s=%s" % (r[0], "W" if t < 0 else "M" if t > 0 else "X")
        if r[0].endswith("=W"): j = list(reversed(j))
    return r, j

if __name__ == "__main__":
    main()
