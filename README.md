
# MW-Classify: A discriminative preordering implementation

## Prerequisites

- Python 2
- LIBLINEAR
    - please set your path instead of `/home/linux/liblinear-221/python`

## Usage

### Preprocessing

```console
$ cat sample/train.ja | [your-parser-here] >sample/train.ja.tree
$ cat sample/predict.ja | [your-parser-here] >sample/train.ja.tree
$ python2 mw-mark.py --tree sample/train.ja.tree --alignment sample/train.ja.align | python2 tree2numbered.py >sample/train.ja.marked
$ python2 mw-mark.py --tree sample/predict.ja.tree --alignment sample/predict.ja.align | python2 tree2numbered.py >sample/predict.ja.marked
$ cat sample/predict.ja.tree | python2 tree2numbered.py >sample/predict.ja.numbered
```

### Training

```console
$ date; python2 mw-classify.py --model m --train_input sample/train.ja.marked --train_output /dev/null; date
Fri Oct 12 10:26:14 DST 2018
loading model ... failed.
[train] sample/train.ja.marked => /dev/null
start training ... saving model ... done.
Fri Oct 12 10:30:44 DST 2018
```

### Prediction

```console
$ date; python2 mw-classify.py --model m --train_input /dev/null --train_output /dev/null --predict_input sample/predict.ja.numbered --predict_output sample/predict.out; date
Fri Oct 12 10:31:31 DST 2018
loading model ... done.
[predict] sample/predict.ja.numbered => sample/predict.out
Fri Oct 12 10:33:41 DST 2018
```

### Postprocessing

```console
$ cat sample/predict.out | cut -f1 | cut -d" " -f1 | python2 mw-modify.py --label /dev/stdin --tree sample/predict.ja.tree | python2 mw-reorder.py | python2 tree2text.py >sample/predict.out.reordered
```

## Reference

```
Sho Hoshino, Yusuke Miyao, Katsuhito Sudoh, Katsuhiko Hayashi, and Masaaki Nagata.
Discriminative Preordering Meets Kendall's Tau Maximization,
In Proceddings of the 53rd Annual Meeting of the Association for Computational Linguistics and the 7th International Joint Conference on Natural Language Processing (ACL-IJCNLP2015), pages 139-144, 2015.
```
