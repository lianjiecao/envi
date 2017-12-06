import subprocess, argparse, binascii, sys, os

def pcap2Nfdata(pcap_fs):
    '''
    Extract and convert pcap files with raw Netflow UDP packets to binary Netflow record data
    If multiple pcap files are given, merge them first.
    '''

    print '\n+ Extracting Netflow payload from raw packets ...'
    pcap_fs = pcap_fs if type(pcap_fs) == list else [pcap_fs]
    nfdata_fs = []

    for pf in pcap_fs:
        hf = '%s_data_hex' % pf
        df = '%s_data_binary' % pf
        # print '  - %s => %s' % (pf, hf)
        sys.stdout.write('  - %s => %s' % (pf, hf))
        ### Extract Netflow records to hex file ###
        if not os.path.isfile(hf):
            cmd = 'tshark -r %s -T fields -e data | tr -d \'\n\' > %s' % (pf, hf)
            ret = subprocess.check_output(cmd, shell=True, executable='/bin/bash')
        sys.stdout.write(' => %s' % df)
        ### Convert hex file to binary file ###
        if not os.path.isfile(df):
            with open(hf, 'r') as hf_f:
                hex_str = hf_f.read()
            # print '  - %s => %s => %s' % (pf, hf, df)
            with open(df, 'w') as df_f:
                df_f.write(binascii.unhexlify(hex_str))
        nfdata_fs.append(df)
        print ''

    return nfdata_fs


def mergPcapFiles(pcap_fs):
    '''
    Merge multiple pcap file before running pcap2Nfdata()
    '''

    if len(pcap_fs) <= 1:
        return pcap_fs[0]
    ### Merge pcap files ###
    pcap_out = os.path.join('/tmp', '-'.join([x.split('/')[-1] for x in pcap_fs]))
    print 'Merging pcap files to [%s]: %s' % (pcap_out, ','.join(pcap_fs))
    cmd = 'mergecap -a -w %s %s' % (pcap_out, ' '.join(pcap_fs))
    ret = subprocess.check_output(cmd, shell=True, executable='/bin/bash')

    return pcap_out


def nfdata2HarpoonConfig(int_len, ipsrc, ipdst, nfdata_fs, int_inc=0):
    '''
    Convert Netflow data to Harpoon intermediate file and then to configuration files 
    '''

    print '\n+ Converting Netflow data to Harpoon configuration files ...'
    if int_len > 600:
        print 'Error: Please specify a IntervalDuration for Harpoon < 600 sec!'
        sys.exit(1)

    int_lens = range(int_len, 601, int_inc) if int_inc > 0 else [int_len]    

    for df in nfdata_fs:
        for l in int_lens:
            ### Generate Harpoon intermediate file ###
            tmp_f = '%s_%d' % (df, l)
            print '  - %s => %s' % (df, tmp_f)
            # sys.stdout.write('  - %s => %s' % (df, tmp_f))
            if not os.path.isfile('%s_flowproc' % tmp_f):
                cmd = 'cat %s | ~/harpoon/selfconf/harpoon_flowproc -i %d -n -w > %s_flowproc' % (df, l, tmp_f)
                subprocess.call(cmd, shell=True, executable='/bin/bash')
            ### Generate Harpoon configuration files ###
            print '  - %s => %s => %s_tcpserver(tcpclient).xml' % (df, tmp_f, tmp_f)
            # sys.stdout.write(' => %s_tcpserver(tcpclient).xml' % tmp_f)
            cmd = 'python ~/harpoon/selfconf/harpoon_conf.py -i %d -S \'%s\' -D \'%s\' -p %s %s_flowproc' % (l, ipsrc, ipdst, tmp_f, tmp_f)
            subprocess.call(cmd, shell=True, executable='/bin/bash')
            
    return


def main():

    parser = argparse.ArgumentParser(description='Convert raw Netflow packets to Harpoon configuration files')

    parser.add_argument('-r', '--raw-pcap',
        action='store',
        dest='pcap_fs',
        type=str,
        help='Pcap files with raw Netflow packets (Ethernet Frames), separated by \',\'',
    )

    parser.add_argument('-m', '--merge-pcap',
        action='store_true',
        dest='merge_pcap_fs',
        help='Merge multiple pcap files before processing',
    )

    parser.add_argument('-f', '--netflow-data',
        action='store',
        dest='nfdata_fs',
        type=str,
        help='Binary files with Netflow data (UDP payload of raw Netflow packets), separated by \',\'',
    )

    parser.add_argument('-i', '--interval-duration',
        action='store',
        dest='int_len',
        type=int,
        default=300,
        help='Interval duration for Harpoon (-i parameter of harpoon_flowproc and harpoon_conf.py)',
    )

    parser.add_argument('-t', '--interval-increment',
        action='store',
        dest='int_inc',
        type=int,
        default=60,
        help='Increment of interval duration for Harpoon to generate configuration files at different granularity',
    )

    parser.add_argument('-d', '--endpoints',
        action='store',
        dest='endpts',
        type=str,
        default='0.0.0.0/32:0.0.0.0/32',
        help='Endpoints of network traffic [ip_src:ip_dst]',
    )


    args = parser.parse_args()

    nfdata_fs = []

    if args.pcap_fs != None:
        if args.merge_pcap_fs:
            pcap_fs = [mergPcapFiles(args.pcap_fs.split(','))]
        else:
            pcap_fs = args.pcap_fs.split(',')
        nfdata_fs.extend(pcap2Nfdata(pcap_fs))

    if args.nfdata_fs != None:
        nfdata_fs.extend(args.nfdata_fs.split(','))

    nfdata2HarpoonConfig(args.int_len, args.endpts.split(':')[0], args.endpts.split(':')[1], nfdata_fs, int_inc=args.int_inc)


if __name__ == '__main__':
    main()
