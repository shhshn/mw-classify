#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools

def main():
    global count
    for line in sys.stdin:
        s = unicode(line).rstrip()
        if s == "": print; continue # sanity check
        s = parse(tokenize(s))
        count = 0
        print numbering(s)

def numbering(node):
    global classias, count
    r = []
    for no, child in enumerate(node):
        if not isinstance(child, list):
            if no == 0: r.append(child); continue
            r.append("%s#%d" % (child, count)); count += 1; continue
        r.append(numbering(child))
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
