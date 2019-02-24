#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys; reload(sys); sys.setdefaultencoding("utf-8")
import itertools
import shared

def main():
    for line in sys.stdin:
        s = unicode(line).rstrip()
        if s == "": print; continue # sanity check
        print " ".join(shared.terminal(shared.parse(shared.tokenize(s))))

if __name__ == "__main__":
    main()
