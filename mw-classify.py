#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools, os.path, argparse
sys.path.append("/home/linux/liblinear-221/python")
import liblinear, liblinearutil

class classias2liblinear:
    m = 2**30 # liblinear 32bit signed integer = [1,2**31] = 30bit
    def extract(self, vec):
        return {v:1 for v in set((abs(hash(f)) % self.m) + 1 for f in vec)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="LIBLINEAR model file")
    parser.add_argument("--train_input", required=True)
    parser.add_argument("--train_output", required=True)
    parser.add_argument("--predict_input")
    parser.add_argument("--predict_output")
    parser.add_argument("--option", default="")
    args = parser.parse_args()
    global count, train, model; train = [[], []]; model = None
    codec = classias2liblinear()
    sys.stderr.write("loading model ... ")
    predict = os.path.isfile(args.model)
    if predict: model = liblinearutil.load_model(args.model)
    sys.stderr.write("%s.\n" % ("failed" if not predict else "done"))
    queue = [(args.train_input, args.train_output)]
    if args.predict_input and args.predict_output:
        queue += [(args.predict_input, args.predict_output)]
    for e, (fin, fout) in enumerate(queue):
        if e == 0 and predict: continue # training is already done
        sys.stderr.write("[%s] %s => %s\n" % ("train" if e == 0 else "predict", fin, fout))
        fin, fout = open(fin), open(fout, "w")
        for line in fin:
            line = unicode(line).rstrip()
            if line == "": continue # sanity check
            s = parse(tokenize(line))
            count = -1; T, W = sentence(s) if "z" in args.option else ([], [])
            count = -1; extract(s, T, W, codec, fout, e > 0, args.option)
        if e == 0 and not predict:
            sys.stderr.write("start training ... ")
            model = liblinearutil.train(liblinear.problem(train[0], train[1]), "-q")
            sys.stderr.write("saving model ... ")
            liblinearutil.save_model(args.model, model)
            sys.stderr.write("done.\n")

def sentence(node):
    T, W = [], []; global count
    if len(node) == 2 and not isinstance(node[1], list):
        count += 1
        return "%s#%d" % (tag(node[0]), count), "%s#%d" % (node[1], count)
    for child in node[1:]:
        tt, ww = sentence(child); T.append(tt); W.append(ww)
    return " ".join(T), " ".join(W)

def extract(node, T, W, codec, fout, predict, option):
    t, w = [], []
    if len(node) == 2 and not isinstance(node[1], list):
        global count; count += 1
        return "%s#%d" % (tag(node[0]), count), "%s#%d" % (node[1], count)
    for child in node[1:]:
        tt, ww = extract(child, T, W, codec, fout, predict, option)
        t.append(tt); w.append(ww)
    if len(node) > 2:
        vec = feature(tag(node[0]), list(tag(x[0]) for x in node[1:]), t, w, node, T, W, option)
        if vec:
            label = "+1" if node[0].endswith("=W") else "-1"
            if not node[0].endswith("=X"):
                out = "%s %s" % (label, " ".join(vec))
                vec = codec.extract(vec)
                vecstr = " ".join("%d" % key for key in vec)
                if predict:
                    global model; labelp = int(liblinearutil.predict([int(label)], [vec], model, "-q")[0][0])
                else:
                    labelp = label
                debug = "%s\t%s\t%d" % (out, tag(node[0]), len(t[0]) + len(t[1]))
                out = "%s %s\t%s %s\t%s" % (labelp, vecstr, label, vecstr, debug)
                if fout is None: print out
                else: fout.write("%s\n" % out); fout.flush()
                if not predict: global train; train[0].append(int(label)); train[1].append(vec)
    return " ".join(t), " ".join(w)

def feature(pt, ct, t, w, node, T, W, option):
    l = int(t[0].split(" ",1)[0].rsplit("#",1)[1])
    r = int(t[-1].rsplit(" ",1)[-1].rsplit("#",1)[1])
    L = int(t[0].rsplit(" ",1)[-1].rsplit("#",1)[1])
    R = int(t[-1].split(" ",1)[0].rsplit("#",1)[1])
    t = list(list(x.rsplit("#",1)[0] for x in tt.split(" ")) for tt in t)
    w = list(list(x.rsplit("#",1)[0] for x in ww.split(" ")) for ww in w)
    out = []
    # feature set (Z) from Li+ 2007
    if "z" in option:
        T = list(x.rsplit("#",1)[0] for x in T.split(" "))
        W = list(x.rsplit("#",1)[0] for x in W.split(" "))
        out += ["ZP;%s" % pt]
        for i in  xrange(len(ct)):
            out += ["ZC%d;%s" % (i, ct[i])]
        out += ["ZLCt;%s" % (T[l-1] if 0 <= (l-1) else None)]
        out += ["ZLCw;%s" % (W[l-1] if 0 <= (l-1) else None)]
        out += ["ZLLt;%s" % t[0][0]]
        out += ["ZLLw;%s" % w[0][0]]
        out += ["ZRRt;%s" % t[-1][-1]]
        out += ["ZRRw;%s" % w[-1][-1]]
        out += ["ZRCt;%s" % (T[r+1] if (r+1) < len(T) else None)]
        out += ["ZRCw;%s" % (W[r+1] if (r+1) < len(W) else None)]
        for tt, ww in itertools.izip(T[::-1], W[::-1]):
            if tt in ("N", "NPR", "PRO", "VB", "VB0", "VB2", "VBI"): break
        out += ["ZHt;%s" % tt]; out += ["ZHw;%s" % ww]
    # boundary (B)
    if "b" not in option:
        for e, (i, j) in enumerate(itertools.izip_longest(xrange(1, len(t[0]) + 1), xrange(1, len(t[-1]) + 1), fillvalue=min(len(t[0]), len(t[-1])) + 1)):
            x = "BLR%dt;%s" % (e, "_".join(t[0][-i:]))
            p = "BLR%dw;%s" % (e, "_".join(w[0][-i:]))
            y = "BRL%dt;%s" % (e, "_".join(t[-1][:j]))
            q = "BRL%dw;%s" % (e, "_".join(w[-1][:j]))
            out += [x, y, p, q, "&".join((x, y)), "&".join((p, q)), "&".join((x, y, p, q))]
        x = "BLRft;%s" % "_".join(t[0])
        p = "BLRfw;%s" % "_".join(w[0])
        y = "BRLft;%s" % "_".join(t[-1])
        q = "BRLfw;%s" % "_".join(w[-1])
        out += [x, y, p, q, "&".join((x, y)), "&".join((p, q)), "&".join((x, y, p, q))]
    # tree tag fragments (F)
    if "f" not in option: out += fragment(node)
    # tree tags (S)
    if "s" not in option: out += ["S;%s" % prittytag(node), "S0;%s" % prittytag(node[1]), "S1;%s" % prittytag(node[2])]
    # tree lexs (L)
    if "l" not in option: out += ["L;%s" % alllex(node, 0)]
    # tree embedding (T)
    if "t" not in option: out += ["T;%s" % embed(node).replace(" ", "")]
    return out

def fragment(node, depth = 0, prefix = "", parent = ""):
    current = "F%s%d;%s" % (prefix, depth, tag(node[0]))
    out = []; out.append(current); out.append("%s%s" % (parent, current))
    for e, child in enumerate(node[1:]):
        if isinstance(child, list):
            if depth == 0 and e == 0: prefix = "L"
            if depth == 0 and e == 1: prefix = "R"
            out += fragment(child, depth + 1, prefix, "%s&" % current)
    return out

def prittytag(node):
    r = []; r.append(tag(node[0]))
    for child in node[1:]:
        if isinstance(child, list): r.append(prittytag(child))
    return "(%s)" % "".join(r)

def alllex(node, depth, prefix = ""):
    r = []
    if len(node) == 2 and not isinstance(node[1], list):
        return node[-1]
    for child in node[1:]:
        r.append(alllex(child, depth + 1))
    return "(%s)" % "".join(r)

def embed(node):
    r = []
    for child in node:
        if not isinstance(child, list): r.append(tag(child)); continue
        r.append(embed(child))
    return "(%s)" % " ".join(r)

def tag(x):
    if x is None: return
    return x[:-2] if x.endswith("=X") or x.endswith("=W") or x.endswith("=M") else x

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
