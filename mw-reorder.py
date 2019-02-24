#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools

def main():
    for line in sys.stdin:
        line = unicode(line).rstrip()
        if line == "": print; continue # sanity check
        s = parse(tokenize(line))
        print reorder(s)

def reorder(node):
    r = []
    for child in node:
        if not isinstance(child, list): r.append(child); continue
        if len(child) > 2:
            if child[0].endswith("=W"):
                child = [child[0]] + list(reversed(child[1:]))
        r.append(reorder(child))
    return "(%s)" % " ".join(r)

def tokenize(sentence):
    return list(x.replace(u"■", u"　") for x in sentence.replace("(", " ( ").replace(")", " ) ").replace(u"　", u"■").split())

def parse(s):
    if len(s) == 0: return # sanity check
    token = s.pop(0)
    if token == "(":
        l = []
        while s[0] != ")":
            sub = parse(s)
            if sub is None: return # sanity check
            l.append(sub)
            if s == []: return # sanity check
        s.pop(0); return l
    elif token == ")": return # sanity check
    else: return token

if __name__ == "__main__":
    main()
