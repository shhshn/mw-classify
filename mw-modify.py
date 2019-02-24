#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools, argparse
import shared

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True, help="(predicted) label")
    parser.add_argument("--tree", required=True, help="parse tree")
    args = parser.parse_args()
    global classias; classias = []
    for line in open(args.label):
        classias.append(unicode(line).rstrip())
    for s in open(args.tree):
        s = unicode(s).rstrip()
        if s == "": print; continue # sanity check
        s = shared.parse(shared.tokenize(s))
        print modify(s)

def modify(node):
    global classias
    r = []
    for child in node[1:]:
        if not isinstance(child, list): r.append(child); continue
        r.append(modify(child))
    new = node[0].rsplit("=",1)[0]
    if len(node) > 2: new += "=W" if int(classias.pop(0)) == 1 else "=M"
    return "(%s)" % " ".join([new] + r)

if __name__ == "__main__":
    main()
