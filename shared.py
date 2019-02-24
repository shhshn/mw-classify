#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools

def pritty(node):
    r = []
    for child in node:
        if not isinstance(child, list): r.append(child); continue
        r.append(pritty(child))
    return "(%s)" % " ".join(r)

def flatten(node):
    r = []
    for child in node:
        if not isinstance(child, list): r.append(child); continue
        r += flatten(child)
    return r

def nonterminal(node):
    if len(node) >= 3:
        r = [node[0]]
    else:
        r = []
    for child in node[1:]:
        if isinstance(child, list): r += nonterminal(child)
    return r

def preterminal(node):
    r = []
    for child in node[1:]:
        if isinstance(child, list): r += preterminal(child)
        else: r.append(node[0])
    return r

def terminal(node):
    r = []
    for child in node[1:]:
        if isinstance(child, list): r += terminal(child)
        else: r.append(child)
    return r

def tau(seq):
    l = list(x for x in seq if x is not None)
    n = len(l); c = n * (n - 1); inc = 0
    if n <= 1: return 0 # irregular definition for Null alignment
    for x, y in itertools.combinations(xrange(n), 2):
        if l[x] < l[y]: inc += 1
    return inc * 4.0 / c - 1

def median(seq):
    l = sorted(x for x in seq if x is not None)
    if l == []: return None
    z, m = divmod(len(l), 2); return l[z] if m else (l[z-1] + l[z]) / 2.0

def tokenize(sentence):
    return list(x.replace(u"■", u"　") for x in sentence.replace("(", u" ( ").replace(")", u" ) ").replace(u"　", u"■").split())

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

