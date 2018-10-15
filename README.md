# ENVI Dataset
This repo includes offline training data and online testing data used in our [ANCS 2018 paper](https://dl.acm.org/citation.cfm?id=3230725). This work was done as part of Lianjie Cao's internship at Hewlett Packard Labs while he was a student at Purdue University.

## Offline Data
```envi/data/offline/``` includes training datasets for IDS [Suricata](https://suricata-ids.org/) and caching proxy [Squid](http://www.squid-cache.org/), each of which contains data collected using 5 different types of homogeneous workload traffic.
For Suricata, ```envi/data/offline/suricata``` contains 5 datasets with different malicious ratios from 0% to 70%, while ```envi/data/offline/squid``` contains 5 dataset with different HTTP response sizes from 10 KB to 100 KB.
Each dataset is stored in a csv file with feature names in the first line and values from line 2. Feature ```scale``` is the label created during data preprocessing.

## Online Data
We leverage an [real-world NetFlow traffic trace](https://www.simpleweb.org/wiki/index.php/Traces#NetFlow_Traces) to generate online testing workload. Since the original trace is huge and spans over 8 days, we extract and average the key informaion such as TCP/UDP packet rate, throughput in Bps/bps, and TCP/UDP flow rate over 3600 seconds. ```envi/data/online/``` contains this information for UDP (to test Suricata) and TCP (to test Squid) traffic. Note that users may need to modulate this infomation (e.g., proportionally increase) to make sure the generated workload do not alway overload or underload the tested VNF. In other words, the ideal testing workload should fluctuate around the system capacity point.

We also include the python scripts to extract the UDP and TCP information from the original NetFlow trace in ```envi/src/utils/```. ```wireshark-common``` and ```tshark``` are required to run the scripts.

