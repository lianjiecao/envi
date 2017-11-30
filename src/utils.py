import sys, subprocess
import numpy as np


stats_f = {
    'mean': np.mean,
    'median': np.median,
    'max': max,
    'min': min,
    'std': np.std,
    # 'first':lambda x: x[0] if type(x) is list else x,
    # 'last':lambda x: x[-1] if type(x) is list else x,
}

proto2key_f = {'udp':'vnf.decoder.udp', 'http':'vnf.app_layer.flow.http'}

def str2float(v):
    if type(v) == list:
        try:
            return [float(x) for x in v]
        except:
            return v
    else:
        try:
            return float(v)
        except:
            return v


def conv2dict(v, s):

    if type(v) == dict:
        return v
    else:
        return {s:v}


def conv2list(v):

    if type(v) == list:
        return v
    else:
        return [v]


def errorMsg(s, logger=None):
    '''
    Print error messages and exit
    '''

    if logger is None:
        print 'Error:', s
    else:
        logger.error(s)
    
    sys.exit(1)


def logMsg(msg, func=None, stderr=False):
    '''
    Print log message for a function
    '''

    if func is not None:
       msg = '[%s] - %s' % (func, msg)

    if stderr:
        sys.stderr.write(msg)
    else:
        print msg


def getDataFileType(f_path):
    '''
    Analyze file path to determine workload protos for data set
    '''

    w_protos = []
    if 'UDP' in f_path or 'udp' in f_path:
        w_protos.append('udp')
    if 'HTTP' in f_path or 'http' in f_path:
        w_protos.append('http')

    return w_protos


def getFilesFromDir(dir_name, key):
    '''
    Return all files with 'key' in 'dir'
    '''

    return subprocess.check_output("ls -tr %s/*%s*" % (dir_name.strip('/'), key), shell=True).split()



def mergeDataFiles(data_fs):
    '''
    Merge multiple data files into one
    '''

    if type(data_fs) is not list or len(data_fs) == 1:
        tmp_f = data_fs[0]
    else:
        ### Merge all training data files if multiple training files are given ###
        tmp_f = '%s.csv' % genFileName(train_fs)
        subprocess.check_output('cat %s > %s' % (train_fs[0], tmp_f), shell=True)
        for f in train_fs[1:]:
            subprocess.check_output('tail -n +2 %s >> %s' % (f, tmp_f), shell=True)

    return tmp_f


def genFileName(file_names):
    '''
    Generate file name from multiple input files
    '''

    if type(file_names) is not list:
        return file_names
    prefix = file_names[0][:file_names[0].find('/')]
    tokens = [x.split('/')[-1].split('-')[2] for x in file_names]
    new_file_name = '%s/%s-%s' % (prefix, file_names[0].split('/')[-1].split('-')[0], '-'.join(tokens))

    return new_file_name


