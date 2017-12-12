#! /usr/bin/python

import argparse, subprocess, json, os, shutil, csv, sys, itertools
import matplotlib
matplotlib.use('Agg')
import pylab as plt


port_proto = {'6':'tcp', '17':'udp'}
proto_port = {'tcp':'6', 'udp':'17'}
marker_labels = ['x', '+', '.', ',', '^']
color_labels = ['g', 'b', 'r', 'y' ,'c', 'm']

def analyzeNetflowTrace(pcap_fs, n_pkts, pts, mode=1):
    '''
    Analyze Netflow trace and decode the first n_pkts netflow raw packets from pcap_fs
    '''
    
    N_pkts = 10000
    pcap_fs = pcap_fs if type(pcap_fs) == list else [pcap_fs]
    pcap_info = {x:[] for x in pcap_fs}
    stats_fs = []
    for pf in pcap_fs:
        net_pkt_avg = {x:{} for x in pts}
        net_vol_avg = {x:{} for x in pts}
        cmd = 'capinfos -caeuSMNTm %s' % pf
        ret = subprocess.check_output(cmd, shell=True)
        ### File name,Number of packets,Capture duration (seconds),Start time,End time
        ### /home/cao/traces/campus_netflow_v5/netflow0,693488,2874.947468,1185457717.131847,1185460592.079315
        pcap_info[pf] = conv2Number(ret.strip().split()[-1].strip().split(','))
        n_pkts = pcap_info[pf][1] if n_pkts == 0 else n_pkts
        f_n_pkts = pcap_info[pf][1] if pcap_info[pf][1] < n_pkts else n_pkts
        if f_n_pkts > 0:
            if mode == 1:
                ### Split large pcap files to smaller ones with N_pkts packets ###
                tmp_dir = '/tmp/splitted_pcaps'
                if os.path.isdir(tmp_dir):
                    shutil.rmtree(tmp_dir)
                os.mkdir(tmp_dir)
                cmd = 'editcap -c %d %s %s/%s' % (N_pkts, pf, tmp_dir, pf.split('/')[-1])
                subprocess.call(cmd, shell=True)
                pkt_cnt = 0
                tmp_pcap_files = sorted(os.listdir(tmp_dir))
                sys.stderr.write('+++ Splitted pcap file into %d pieces for %s packets ...\n' % (len(tmp_pcap_files), ' '.join(pts)))
                ### Read packets from each splitted pcap ###
                for tmp_pf in tmp_pcap_files:
                    sys.stderr.write('--- Processing %s ...\n' % tmp_pf)
                    cmd = 'tshark -r %s/%s -d udp.port==9500,cflow -Tjson -c %d' % (tmp_dir, tmp_pf, min(f_n_pkts-pkt_cnt, N_pkts))
                    ret = subprocess.check_output(cmd, shell=True)
                    pkts = json.loads(ret)
                    pkt_cnt += len(pkts)
                    decodeNetflowPkts(pkts, net_pkt_avg, net_vol_avg, N_pkts, pts)
                    if pkt_cnt >= f_n_pkts:
                        break
            if mode == 2:
                ### Read a packet a time (smaller memory footprint) ###
                for pkt_idx in range(1, int(f_n_pkts) + 1):
                    cmd = 'tshark -r %s -d udp.port==9500,cflow -Tjson -Y frame.number==%d -c %d' % (pf, pkt_idx, pkt_idx)
                    ret = subprocess.check_output(cmd, shell=True)
                    pkts = json.loads(ret)
                    decodeNetflowPkts(pkts, net_pkt_avg, net_vol_avg, 1, pts)
        n_pkts -= f_n_pkts
        for pt in pts:
            out_f = '%s_%s.stats' % (pf, pt)
            dumpStats(out_f, net_pkt_avg[pt], net_vol_avg[pt])
            stats_fs.append(out_f)

    return stats_fs


def dumpStats(out_f, net_pkt_avg, net_vol_avg):
    with open(out_f, 'w') as of:
        of.write('time,pkts,bytes\n')
        for sec in sorted(net_pkt_avg.keys()):
            of.write('%d,%d,%d\n' % (sec, net_pkt_avg[sec], net_vol_avg[sec]))

    sys.stderr.write('+++ Dumped stats to %s\n' % out_f)
    return


def decodeNetflowPkts(pkts, net_pkt_avg, net_vol_avg, max_n_pkts, pts):
    '''
    Decode Netflow packets
    '''

    if len(pkts) <= 0:
        return

    for pkt_idx in range(min(len(pkts), max_n_pkts)):
        n_flows = conv2Number(pkts[pkt_idx]['_source']['layers']['cflow']['cflow.count'])
#        print '%d flows found in Netflow packet %d' % (n_flows, pkt_idx)
        ### Read each flow record ###
        for rec_idx in range(1, int(n_flows)+1):
            pdu = pkts[pkt_idx]['_source']['layers']['cflow']['pdu %d/%d' % (rec_idx, n_flows)]
            ### TCP flows ###
            if pdu['cflow.protocol'] in [proto_port[x] for x in pts]:
                pt = port_proto[pdu['cflow.protocol']]
                flow_len = 1 if int(float(pdu['cflow.timedelta'])) == 0 else int(float(pdu['cflow.timedelta']))
                flow_pkt = int(pdu['cflow.packets'])
                flow_vol = int(pdu['cflow.octets']) - flow_pkt * 40
                ### Update pkt and vol info for each sec of the flow duration ###
                for sec in range(int(float(pdu['cflow.timedelta_tree']['cflow.timestart'])), \
                        int(float(pdu['cflow.timedelta_tree']['cflow.timestart'])) + 1 ):
                    net_pkt_avg[pt][sec] = net_pkt_avg[pt].get(sec, 0) + flow_pkt / flow_len
                    net_vol_avg[pt][sec] = net_vol_avg[pt].get(sec, 0) + flow_vol / flow_len

    return


def conv2Number(strings):
    '''
    Convert string to numbers if possible
    '''
    
    if type(strings) == list:
        numbers = []
        for s in strings:
            try:
                numbers.append(float(s))
            except:
                numbers.append(s)

        return numbers
    else:
        try:
            return float(strings)
        except:
            return numbers


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


def getFilesFromDir(dir_name, key=''):
    '''
    Get all files with key in dir_name
    '''

    files_all = os.listdir(dir_name)

    return [os.path.join(dir_name, x) for x in files_all if key in x]


def calcMean(stats_1sec, avg_int):
    '''
    Calculate mean values over intv seconds
    '''

    stats_avg = {} # {sec:[pkt_rate, byte_rate]}
    stats_avg_plot = {'Time':[], 'Packet_Per_Second':[], 'Bytes_Per_Second':[], 'Mbps':[]}
    times = sorted(stats_1sec.keys())
    if avg_int > times[-1] - times[0]:
        sys.stderr.write('Error: interval value is large then trace duration: [%d:%d]\n' % (times[0], times[-1]))
        sys.exit(1)
    for sec in range(times[0], times[-1], avg_int):
        stats_avg[sec] = [sum([stats_1sec[t][x] for t in range(sec, sec + min(avg_int, times[-1]-sec))]) / avg_int \
            for x in range(len(stats_1sec[sec]))]

    sys.stderr.write('+++++ Stats over %d seconds +++++\n' % avg_int)
    print 'time,pkt_%dsec,byte_%dsec,mbps_%dsec' % (avg_int, avg_int, avg_int)
    for sec in sorted(stats_avg.keys()):
        mbps_val = float(stats_avg[sec][-1]) * 8 / 1000000
        print '%d,%s,%.4f' % (sec, ','.join(map(str, stats_avg[sec])), mbps_val)
        stats_avg_plot['Time'].append(sec)
        stats_avg_plot['Packet_Per_Second'].append(stats_avg[sec][0])
        stats_avg_plot['Bytes_Per_Second'].append(stats_avg[sec][1])
        stats_avg_plot['Mbps'].append(mbps_val)

    return stats_avg_plot


def plotMean(stats_avg, fig_name):

    markers = itertools.cycle(marker_labels[:len(stats_avg)])
    colors = itertools.cycle(color_labels[:len(stats_avg)])
    int_vals = stats_avg.keys()
    data_labels = [x for x in stats_avg[int_vals[0]].keys() if x != 'Time']

    for key in data_labels:
        fig, ax = plt.subplots()
        for int_val in int_vals:
            plt.plot(stats_avg[int_val]['Time'], stats_avg[int_val][key], color=colors.next(), label='%s_%dsec' % (key, int_val), lw=2)
            #marker=markers.next(), markersize=7, mew=2

#        plt.xticks(a_ticks, fontsize=14)
#        plt.yticks(a_ticks, fontsize=14)
        plt.xlabel('Time (second)', fontsize=14)
        plt.ylabel(key, fontsize=14)
        # plt.title('Receiver operating characteristic')
        ax.legend(loc='upper right', ncol=1, fontsize=12)
        # ax.set_title(makeFigTitle(outP), fontsize=18)
        plt.grid()

        plt.savefig('%s_%s.png' % (fig_name, key), bbox_inches='tight')


def main():
    parser = argparse.ArgumentParser(description='Parse Netflow raw packets')
    parser.add_argument('-p', '--pcap-files',
        dest='pcap_fs',
        action='store',
        type=str,
#        required=True,
        help='pcap files of Netflow packets, separated by \',\''
    )

    parser.add_argument('--pcap-dirs',
        dest='pcap_dirs',
        action='store',
        type=str,
#        required=True,
        help='Directories including pcap files of Netflow packets, separated by \',\''
    )

    parser.add_argument('-s', '--stats-files',
        action='store',
        dest='stats_fs',
        type=str,
        help='Stats files, separated by \',\'',
    )

    parser.add_argument('--stats-dirs',
        dest='stats_dirs',
        action='store',
        type=str,
#        required=True,
        help='Directories including stats files of Netflow packets, separated by \',\''
    )

    parser.add_argument('-t', '--protos',
        action='store',
        dest='protos',
        type=str,
        default='tcp',
        help='Protocols to extract, separated by \',\': udp, tcp',
    )

    parser.add_argument('-i', '--avg-interval',
        action='store',
        dest='avg_int',
        type=str,
#        default=60,
        help='During of interval to compute mean',
    )

    parser.add_argument('-n', '--num-pkts',
        dest='n_pkts',
        action='store',
        type=int,
        default=0,
        help='Number of packets to decode'
    )

    parser.add_argument('-m', '--proc-mode',
        dest='proc_mode',
        action='store',
        type=int,
        default=1,
        help='Processing mode of Netflow trace file: 1, read all packets; 2, read one packet a time'
    )

    parser.add_argument('-f', '--out-figure',
        dest='out_fig',
        action='store',
        type=str,
        help='Figure file name'
    )

    args = parser.parse_args()
    stats_fs = []
    pcap_fs = []
    protos = args.protos.split(',')

    if args.stats_fs is not None:
        stats_fs.extend(args.stats_fs.split(','))
 
    if args.stats_dirs is not None:
        for s_dir in args.stats_dirs.split(','):
            stats_fs.extend(getFilesFromDir(s_dir, key='%s.stats' % protos[0]))

    if args.pcap_fs is not None:
        pcap_fs.extend(args.pcap_fs.split(','))
 
    if args.pcap_dirs is not None:
        for p_dir in args.pcap_dirs.split(','):
            pcap_fs.extend(getFilesFromDir(p_dir, key='netflow'))

    if len(stats_fs) > 0 and args.avg_int is None:
        args.avg_int = '100'

#    if len(pcap_fs) > 0:
#        stats_fs.extend(analyzeNetflowTrace(pcap_fs, args.n_pkts, args.protos.split(','), mode=args.proc_mode))

    print pcap_fs, stats_fs
    if args.avg_int is not None:
        if len(stats_fs) <= 0:
            print 'Error: Please specify -p or -s!'
            sys.exit(1)
        stats_1sec = readStatsFiles(stats_fs)
        stats_avg = {}
        for avg_int in [int(x) for x in args.avg_int.split(',')]:
            stats_avg[avg_int] = calcMean(stats_1sec, avg_int)
        if args.out_fig is not None:
            plotMean(stats_avg, args.out_fig)


if __name__ == '__main__':
    main()
