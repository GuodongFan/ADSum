#!/usr/bin/env python3

from __future__ import print_function

import argparse
import sys
from collections import defaultdict
import glob

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine predictions.')
    parser.add_argument('--method', help='Change combination method', default='vote', choices=['vote', 'union', 'intersect'])
    parser.add_argument('predictions', help='Files containing the predictions.')
    args = parser.parse_args()

    files = glob.glob(args.predictions)
    print(files)
    #files = ['data/gitter/Microsoft/TypeScript/content.annotation.txt0', 'data/gitter/Microsoft/TypeScript/content.annotation.txt1']
    counts = {}
    all_nums = {}
    for filename in files:
        for line in open(filename):
            line = line.strip()
            if line.startswith("#"):
                continue
            name, values = line.split(":")
            #name, values = 'gitter', line
            if args.method != 'intersect':
                nums = [int(v) for v in values.split() if v != '-']
                nums.sort(reverse=True)
                info = counts.setdefault((name, nums[0]), {})
                if len(nums) > 1:
                    for num in nums[1:]:
                        if num not in info:
                            info[num] = 0
                        info[num] += 1
                else:
                    if nums[0] not in info:
                        info[nums[0]] = 0
                    info[nums[0]] += 1
                seen = all_nums.setdefault(name, set())
                for num in nums:
                    seen.add(num)
            else:
                clusters = counts.setdefault(name, {})
                values = [int(v) for v in values.split()]
                values.sort()
                cluster = tuple(values)
                if cluster not in clusters:
                    clusters[cluster] = 0
                clusters[cluster] += 1
                seen = all_nums.setdefault(name, set())
                for num in cluster:
                    seen.add(num)

    if args.method != 'intersect':
        out_file = open('data/gitter/ethereum/welcome/content.annotation.txt', 'w')
        for name, src in counts:
            info = counts[name, src]
            options = [(count, num) for num, count in info.items()]
            options.sort(reverse=True)
            keep = []
            if options[0][1] == src:
                keep.append(src)
            elif args.method == 'union':
                keep = [n for c, n in options if n != src]
            else:
                if options[0][0] == len(args.predictions):
                    keep = [n for c, n in options if c >= len(args.predictions) and n != src]
                else:
                    keep.append(options[0][1])

            for num in keep:
                print("{}:{} {} -".format(name, src, num))
                out_file.write("{} {} -".format(src, num))
                out_file.write('\n')
        out_file.close()
    else:
        for name in counts:
            seen = all_nums[name]
            clusters = counts[name]
            ordered = []
            for cluster in clusters:
                count = clusters[cluster]
                if count >= len(args.predictions):
                    ordered.append((count, cluster))
            ordered.sort()
            # Go through from most agreement to least, and include all of the
            # cluster that hasn't been used yet
            included = set()
            for _, cluster in ordered:
                if all(n not in included for n in cluster):
                    print("{}:{}".format(name, ' '.join([str(n) for n in cluster])))
                    for num in cluster:
                        included.add(num)
            for num in seen:
                if num not in included:
                    print("{}:{}".format(name, num))

