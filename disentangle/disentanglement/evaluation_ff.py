# !/usr/bin/env python3

from __future__ import print_function

import argparse
import logging
import sys
import pandas as pd
import numpy as np

def find(x, parents):
    while parents[x] != x:
        parent = parents[x]
        parents[x] = parents[parent]
        x = parent
    return x


def union(x, y, parents, sizes):
    # Get the representative for their sets
    x_root = find(x, parents)
    y_root = find(y, parents)

    # If equal, no change needed
    if x_root == y_root:
        return

    # Otherwise, merge them
    if sizes[x_root] > sizes[y_root]:
        parents[y_root] = x_root
        sizes[x_root] += sizes[y_root]
    else:
        parents[x_root] = y_root
        sizes[y_root] += sizes[x_root]


def union_find(nodes, edges):
    # Make sets
    parents = {n: n for n in nodes}
    sizes = {n: 1 for n in nodes}

    for edge in edges:
        union(edge[0], edge[1], parents, sizes)

    clusters = {}
    for n in parents:
        clusters.setdefault(find(n, parents), set()).add(n)
    cluster_list = list(clusters.values())
    return cluster_list

def correct_start(gold, auto, do_end=False):
    # P/R/F for identifying starting messages
    gold_starts = set(gold)
    auto_starts = set(auto)

    match = len(gold_starts.intersection(auto_starts))

    if len(auto_starts) == 0:
        return 0, 0, 0

    p = 100 * match / len(auto_starts)
    r = 100 * match / len(gold_starts)
    f = 0.0
    if match > 0:
        f = 2 * p * r / (p + r)
    prefix = "End" if do_end else "Start"
    print("{:5.2f}   {} Precision".format(p, prefix))
    print("{:5.2f}   {} Recall".format(r, prefix))
    print("{:5.2f}   {} F-score".format(f, prefix))
    return r, p, f


def get_clusters(file_name):
    global all_clusters, source, cluster
    filename = ""
    nodes = {}
    edges = {}
    cutoffs = {}
    all_clusters = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if ':' in line:
            filename, line = line.split(':')

        parts = [int(v) for v in line.strip().split() if v != '-']
        source = max(parts)
        nodes.setdefault(filename, set()).add(source)
        parts.remove(source)
        for num in parts:
            edges.setdefault(filename, []).append((source, num))
            nodes.setdefault(filename, set()).add(num)

        # A cutoff based on the min source is used to get consistent sets for evaluation
        if filename not in cutoffs:
            cutoffs[filename] = source
        else:
            cutoffs[filename] = min(source, cutoffs[filename])
    for filename in nodes:
        cutoff = cutoffs[filename]
        clusters = union_find(nodes[filename], edges[filename])
        for cluster in clusters:
            vals = [v for v in cluster if v >= cutoff or args.no_cutoff]
            # vals.sort()
            # print(filename + ":" + " ".join(vals))

            all_clusters.append(vals)
    return all_clusters


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert a conversation graph to a set of connected components (i.e. threads).')
    parser.add_argument("--no-cutoff", help="Do not enforce a cutoff based on source numbers", action="store_true")
    args = parser.parse_args()

    all_threads_auto = get_clusters('./Typescript.annotation.txt')
    all_threads_gold = get_clusters('./proposed_dataset/original_format/test_Typescript/Typescript.annotation.txt')


    R, P, F = 0, 0, 0
    for idx, thread in enumerate(all_threads_gold):
        max_len = 0
        max_cluster = []
        for cluster in all_threads_auto:
            this_len = len(set(thread).intersection(cluster))
            if this_len > max_len:
                max_len = this_len
                max_cluster = cluster

        temp_r, temp_p, temp_f = correct_start(thread, max_cluster)
        R += temp_r
        P += temp_p
        F += temp_f

    print("{:5.2f} Precision".format(R/idx))
    print("{:5.2f} Recall".format(P/idx))
    print("{:5.2f} F-score".format(F/idx))
