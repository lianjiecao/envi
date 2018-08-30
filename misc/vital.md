# NFV-VITAL: VNF Performance Characterization Framework

## Basics
### Motivation

NFV-VITAL is a framework to generate different types of workload for testing the performance of various VNFs. It also can be used for generating offline training data and run online experiments for ENVI project with VNF-specific monitoring agent. It currently supports performance testing for Snort, Suricata and Squid.
Workload generation, VNF monitoring and scaling decisions (ENVI) are the three main parts. 

### Options
```sh
ubuntu@exp-ctl:~/nfv-vital$ ./idsExperiment.py -h
usage: idsExperiment.py [-h] [--config CONF] [--exp-mode EXP_MODE]
                        [--train-files TRAIN_FS] [--baseline BASELINE]

Performance experiments for IDS

optional arguments:
  -h, --help            show this help message and exit
  --config CONF, -f CONF
                        Experiment configuration file
  --exp-mode EXP_MODE, -m EXP_MODE
                        Experimental mode: homo, hybrid
  --train-files TRAIN_FS
                        Raw data files of vital experiment for training,
                        separated by ","
  --baseline BASELINE, -b BASELINE
                        Use baseline of CPU threshold to make scaling
                        decisions
```

```--config``` is the experiment configuration file contains information of VNF, orchestrator, monitor and, most importantly, workload.

**Example commands**
- Run multiple types of homogeneous traffic for Suricata and collect data sets for offline training
    ```sh
    suricata-test-new.yaml
        ...
        udp:
            script: /home/ubuntu/nfv-vital/scripts/ids/start_udp_hping3_tc.sh # For UDP
            unit: mal
            types: [0, 10, 30, 50, 70] # Malicious traffic proportion
            vnf_caps: 
            max_rates:
            init_rates: [5000.0] # Number of UDP pkts per sec
            rate_add: [5000.0] # Default incremental step size for UDP pkt rate
            rate_ratio_range: [0.4, 1.2] # Range to adjust request rate after slow start
            rate_adj_file:
            rate_file:
            client_conf:
            server_conf:
            instances:
                clients:
                    - {type: main, name: ids-snd-2, username: ubuntu, ctl_ip: '192.168.1.22', data_ip: '192.168.2.22'}
                    - {type: backup, name: ids-snd-3, username: ubuntu, ctl_ip: '192.168.1.23', data_ip: '192.168.2.23'}
                    - {type: main, name: ids-snd-4, username: ubuntu, ctl_ip: '192.168.1.24', data_ip: '192.168.3.24'}
                    - {type: backup, name: ids-snd-5, username: ubuntu, ctl_ip: '192.168.1.25', data_ip: '192.168.3.25'}
                servers:
                    - {type: main, name: ids-rcv-2, username: ubuntu, ctl_ip: '192.168.1.32', data_ip: '192.168.2.32'}
                    - {type: main, name: ids-rcv-2, username: ubuntu, ctl_ip: '192.168.1.32', data_ip: '192.168.3.32'}
        ...
        
    $ screen -L -m ./idsExperiment.py --config suricata-test-new.yaml --exp-mode homo
    ```
- Run workload from a rate file (modulate traffic around VNF capacity) for Suricata with 0% malicious traffic
    ```sh
    suricata-test-new.yaml
        ...
        udp:
            script: /home/ubuntu/nfv-vital/scripts/ids/start_udp_hping3_tc.sh # For UDP
            unit: mal
            types: [0] # Malicious traffic proportion
            vnf_caps: [55344]
            max_rates:
            init_rates: [5000.0] # Number of UDP pkts per sec
            rate_add: [5000.0] # Default incremental step size for UDP pkt rate
            rate_ratio_range: [0.4, 1.2] # Range to adjust request rate after slow start
            rate_adj_file:
            rate_file: /home/ubuntu/nfv-vital/netflow_trace/netflow0-183_3600_udp_flow.stats
        ...
        
    $ screen -L -m ./idsExperiment.py --config suricata-test-new.yaml --exp-mode homo
    ```
- Run hybrid HTTP traffic of multiple response sizes for Squid and compare scaling decisions of baseline and neural network
    ```sh
    squid-test-new.yaml
        ...
        http:
            script: /home/ubuntu/nfv-vital/scripts/squid/start_http_web-polygraph_multi_size_proxy_remote.sh # Hybrid f_size from NetFlow
            unit: KB
            types: [50, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # HTTP response size in KB
            vnf_caps: [2000, 3800, 3400, 2400, 2100, 2000, 1900, 1500, 1300, 1500, 1400, 1000] # VNF capacity in requests/sec
            max_rates: [8000]
            init_rates: [200] 
            rate_add: [200] 
            rate_ratio_range: [0.5, 1.0] # Range to adjust request rate after slow start
            rate_adj_file: /tmp/webpolygraph_load_factors.txt # On workload client instances
            rate_file: /home/ubuntu/nfv-vital/netflow_trace/netflow0-183_3600_tcp_flow.stats
            client_conf:
            server_conf:
            instances:
                clients:
                    - {type: main, name: ids-snd-1, username: ubuntu, ctl_ip: '192.168.1.21', data_ip: '192.168.3.21'}
                servers:
                    - {type: main, name: ids-rcv-1, username: ubuntu, ctl_ip: '192.168.1.31', data_ip: '192.168.3.31'}

    $ screen -L -m ./squidExperiment.py --baseline --config squid-test-new.yaml --exp-mode hybrid --train-files squid-1-HTTP-10KB-app-metric.log
    ```

### Output
VITAL collects VNF-level and infras-level data and dumps them to a output directory. ```xxx-app-metric.log``` and ```xxx-infras-metric.log``` are the two files with monitoring data.
```sh
-rw-rw-r-- 1 ubuntu ubuntu  554 Nov 13  2017 ids-snd-2-UDP-0mal.log
-rw-rw-r-- 1 ubuntu ubuntu  554 Nov 13  2017 ids-snd-4-UDP-0mal.log
-rw-rw-r-- 1 ubuntu ubuntu 7.2M Nov 13  2017 ids-1-UDP-0mal-infras-raw.log
-rw-rw-r-- 1 ubuntu ubuntu 1.1M Nov 13  2017 ids-1-UDP-0mal-app-metric.log
-rw-rw-r-- 1 ubuntu ubuntu 385K Nov 13  2017 ids-1-UDP-0mal-infras-metric.log
```
VITAL collects one data point for each monitoring interval T (T = 10 seconds by default) and makes actions (e.g., scaling decisions, resource allocation, etc) for every time window W (W = nT, n = 10 by default). Therefore, ```xxx-app-metric.log``` and ```xxx-infras-metric.log``` files follow the format:

Line 1: feature names separated by ";"

Line 2: feature values collected during W1 (values for each T are separated by ",") for all features (value of features separated by ";")

Line 3: same set of values collected during W2

Example selected from an infras log file:
```sh
cpu;cpu_0;eth0_rcv_byte;eth0_rcv_pkt;eth0_snd_byte;eth0_snd_pkt;
42.0,20.0,19.0,18.0,14.0,13.0,12.5,16.0,13.0,13.5;42.0,20.0,19.0,18.0,14.0,13.0,12.5,16.0,13.0,13.5;1551,0,0,0,0,0,0,0,0,0;6,0,0,0,0,0,0,0,0,0;1163,0,0,0,0,0,0,0,0,0;6,0,0,0,0,0,0,0,0,0;
18.0,24.0,23.5,24.0,24.5,23.0,24.0,23.5,23.0,23.0,24.0;18.0,24.0,23.5,24.0,24.5,23.0,24.0,23.5,23.0,23.0,24.0;1868,4,0,0,0,0,0,0,0,0,476;8,0,0,0,0,0,0,0,0,0,2;2092,6,0,0,0,0,0,0,0,0,910;8,0,0,0,0,0,0,0,0,0,2;
34.0,33.0,33.0,34.5,35.0,34.0,34.0,33.5,33.5,33.5;34.0,33.0,33.0,34.5,35.0,34.0,34.0,33.5,33.5,33.5;1415,0,0,0,0,0,0,0,0,0;6,0,0,0,0,0,0,0,0,0;1295,0,0,0,0,0,0,0,0,0;6,0,0,0,0,0,0,0,0,0;
...
```

### Structure
VITAL includes three types of codes: Python code for overall controlling, yaml files for experiment configuration, and bash code for workload and VNF controlling.

- ```nfv-vital/nfv_vital.py``` includes base classes like ```VNF```, ```WorkloadGenerator```, ```Orchestrator```, ```VNFMonitor``` and ```Experiment```.
- ```nfv-vital/idsExperiment.py``` includes class ```IDSExperiment``` extending ```Experiment``` with methods for running Suricata experiments.
- ```nfv-vital/squidExperiment.py``` includes class ```SquidExperiment``` extending ```IDSExperiment``` for Squid experiments.
- ```envi/src/mlPipeLine.py``` includes class ```MLPipeLine``` for machine learning pipelines used in ENVI.
- ```envi/src/vital_sim.py``` includes methods for simulating online process in ENVI.
- ```envi/src/utils.py``` includes some utility functions.
- ```nfv-vital/suricata-test-new.yaml```, ```nfv-vital/squid-test-new.yaml``` are the latest experiment configurations files for Suricata and Squid.
- ```nfv-vital/scripts/ids``` and ```nfv-vital/scripts/squid``` include control scripts to start/stop VNF and workload generator.

### Experiment Mode and Workload Generation
VITAL is capable of generating homogeneous and hybrid workload traffic in terms of composition and rate. Depending on the VNF, hybrid workload traffic can be a combination of different protocols or different parameters of the same protocol. For instance, user can combine UDP, TCP and HTTP traffic for IDS experiments. User may also specify different parameters for each protocol (malicious ratio for UDP and response size for HTTP). But only one parameter can be used for each ```update_interval```. For instance, user can generate HTTP traffic with 20 KB response size and UDP traffic with 10% malicious traffic at the same time, but it is impossible to have UDP traffic with 10% and 30% malcious traffic together. User may change malicious traffic ratio in the next interval.

- **Homogeneous workload** (```--exp-mode homo```) is usually used for collecting offline training data. User may specify multiple protocols and parameters for each protocol, but they will be used sequentially (one <protocol, parameter> a time). It starts with a "slow_start" phase (if ``` vnf_caps``` is not set in experiment configuration) to detect the VNF system capacity of the current workload type, then it enters "random" phase in which rate is computed based on a random ratio (generated based on ```rate_ratio_range```) of the detected VNF capacity value.

- **Hybrid workload** (```--exp-mode homo```) is used for ENVI online testing which requires either multiple protocols (e.g., combine UDP, TCP and HTTP traffic for Suricata) or different protocol parameters (e.g., change response size of HTTP traffic for Squid). In hybrid mode, if ``` vnf_caps``` is not set, it will automatically excute the "slow_start" mode for each <protocol, parameter> workload type to figure out the VNF capacity. The only differences are for each interval VITAL randomly pick a parameter for each protocol and the random ratio will be further splitted for each specified protocol.

- **Workload rate** in the two experiment modes is either incremental ("slow start" phase) or randomly generated around VNF capacity. However, user can also specify predefined rates in a rate file ```rate_file``` which is referred as "custom rate" mode. ```/home/ubuntu/nfv-vital/netflow_trace/netflow0-183_3600_udp_flow.stats``` is an example rate file extracted from a [Netflow trace](https://www.simpleweb.org/wiki/index.php/Traces#NetFlow_Traces). Custom rate does not conflict homogeneous and hybrid workload modes. It simply replace the random rate computation method. But in order use "custom rate" mode with a rate file, user needs to specify workload parameters ```types``` and ```vnf_caps```. VITAL modulate the given custom rates (using multipliers and offsets) to make sure VNF will be operated around the capacity point. The motivation behind this is to artifically introduce VNF overload and make scaling decisions necessary (for testing ENVI). User may change the workload modulation parameters in ```getCustomRate()```. If VNF capacities are not specified, the original values in the rate file will be used.

### Scaling VNFs

Scaling decisions are introduced by ENVI, along with VNF monitoring agents. To use this function, user needs to specify training data sets via option ```--train-files```. Then a ```MLPipeLine``` will be trained and used for making scaling decisions every time a monitoring sample (VNF-level and infras-level) is collected. User may also use ```--baseline``` to specify a CPU threshold to make scaling decisions. If both ```--train-files``` and ```--baseline``` are not specified, not scaling decisions will be made. VNF may be overloaded depending on workload modulation (for "custom rate" mode). 

### Notes
- Currently, to use the ```--baseline``` scaling method, user also needs to specify ONLY ```--train-files```, but only baseline scaling decisions will be executed. Neural network results are for comparison only.
- VITAL starts the control process on controller instance, VNF processes on VNF instances, workload generation process on sender and receiver instances. Depending on the workload generator, there can be different ways to control workload rate. For instance, hping3 is the workload generator for IDSes. We use tc rules to control the packet rate going out of the sender instances. Web polygraph generates HTTP traffic for Squid and we write new rate values to a rate file to interactively control HTTP request rate.





