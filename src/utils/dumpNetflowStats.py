#! /usr/bin/python

import argparse, csv, sys

def readStatsFiles(stats_fs):
    '''
    Reader stats info from files with format:
    time,pkts,bytes
    '''

    stats_info = {} # {time_stamp:[pkts, bytes]}
    prev_time = 0
    
    for sf in stats_fs:
        with open(sf, 'r') as f:
            reader = csv.reader(f)
            for l,row in enumerate(reader):
                if l == 0:
                    keys = row
                    continue
                time = int(row[0])
                stats_info[time] = [x+y for x,y in zip(stats_info.get(time, [0] * (len(row) - 1)), [int(x) for x in row[1:]])]
                if prev_time > 0 and time - prev_time > 1:
                    for sec in range(prev_time+1, time):
                        stats_info[sec] = stats_info.get(sec, [0] * (len(row) - 1))
                prev_time = time

    return stats_info


def calcMean(stats_1sec, avg_int):
    '''
    Calculate mean values over intv seconds
    '''

    stats_avg = {}
    times = sorted(stats_1sec.keys())
    if avg_int > times[-1] - times[0]:
        print 'Error: interval value is large then trace duration: [%d:%d]' % (times[0], times[-1])
        sys.exit(1)
    for sec in range(times[0], times[-1], avg_int):
        stats_avg[sec] = [sum([stats_1sec[t][x] for t in range(sec, sec + min(avg_int, times[-1]-sec))]) / avg_int \
            for x in range(len(stats_1sec[sec]))]       

    print 'time,pkt_%dsec,byte_%dsec,mbps_%dsec' % (avg_int, avg_int, avg_int)
    for sec in sorted(stats_avg.keys()):
        print '%d,%s,%d' % (sec, ','.join(map(str, stats_avg[sec])), stats_avg[sec][-1] * 8 / 1000000)


def main():
    parser = argparse.ArgumentParser(description='Dump stats info from parseNetfrom.py output')

    parser.add_argument('-r', '--stats-files',
        action='store',
        dest='stats_fs',
        type=str,
        help='Stats files, separated by \',\'',
    )

    parser.add_argument('-i', '--avg-interval',
        action='store',
        dest='avg_int',
        type=int,
        default=60,
        help='During of interval to compute mean',
    )

    args = parser.parse_args()

    stats_1sec = readStatsFiles(args.stats_fs.split(','))
    calcMean(stats_1sec, args.avg_int)


if __name__ == '__main__':
    main()
