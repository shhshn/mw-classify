#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools, argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignment", required=True, help="word alignment")
    parser.add_argument("--tree", required=True, help="parse tree")
    args = parser.parse_args()                
    alltau = []
    for align, s in itertools.izip(open(args.alignment), open(args.tree)):
        align = unicode(align).rstrip()
        if align == "": print; continue # sanity check
        align = [map(int, x.split("-")) for x in align.split(" ")]
        s = parse(tokenize(unicode(s).rstrip()))
        i, ii = index(s, align)
        print "%s\t%s\t%s\t%s" % (tau(i), i, ii, pritty(s))
        alltau.append(tau(i))
    sys.stderr.write("%s %s %s %s\n" % ("avg = %f" % (sum(alltau) / len(alltau)), "med = %f" % median(alltau), "min = %f" % min(alltau), "max = %f" % max(alltau))); sys.stderr.flush()
    dist = {}
    for t in alltau:
        v = "%.1f" % t
        if v == "-0.0": v = "0.0"
        v = float(v)
        if v not in dist: dist[v] = 0
        dist[v] += 1
    for v in xrange(-10, 10 + 1, 1):
        v = float(v / 10.0)
        sys.stderr.write("%.1f %d\n" % (v, dist[v] if v in dist else 0))
        sys.stderr.flush()

def pritty(node):
    r = []
    for child in node:
        if not isinstance(child, list): r.append(child); continue
        r.append(pritty(child))
    return "(%s)" % " ".join(r)

def index(node, align):
    i = []; ii = []
    for no, child in enumerate(node):
        if not isinstance(child, list):
            if no != 0:
                count = int(child.rsplit("#", 1)[-1])
                iii = []
                for f, e in align:
                    if f == count: iii.append(e)
                i.append(median(iii)); ii.append(median(iii)); 
            continue
        c, cc = index(child, align); i += c; ii.append(cc)
    return i, ii

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
