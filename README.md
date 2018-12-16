# ENVI Dataset
This repo includes offline training data and online testing data used in our [ANCS 2018 paper](https://dl.acm.org/citation.cfm?id=3230725). For more details about motivation, implementation and experimentation, please refer to our paper. This work was done as part of Lianjie Cao's internship at [Hewlett Packard Labs](https://www.labs.hpe.com/) while he was a student at [Purdue University](https://www.cs.purdue.edu/). 

There are two types of datasets in ENVI: VNF workload generation information and VNF feature information. Workload generation information is the dataset used by workload generators to generate network traffic such as packet rate, HTTP request rate and so forth. VNF feature information is the dataset collected when VNF processes the generated workload traffic including information of infrastructure-level and VNF-level features. The VNF feature information is used to either train the initial neural network model during the offline training stage or make scaling decisions (```scale``` and ```not scale```) and update the current neural network model.
This repository includes VNF feature information (Squid and Suricata) for offline training stage and workload generation information (TCP and UDP) for online updating stage.

## Offline Data
```envi/data/offline/``` includes selected training datasets for IDS [Suricata](https://suricata-ids.org/) and caching proxy [Squid](http://www.squid-cache.org/), each of which contains data collected using 5 different types of homogeneous workload traffic.

For Suricata, ```envi/data/offline/suricata``` contains 5 datasets with different malicious ratios from 0% to 70%, while ```envi/data/offline/squid``` contains 5 dataset with different HTTP response sizes from 10 KB to 100 KB.

Each dataset is stored in a csv file with feature names in the first line and values from line 2. Features with ```infras.``` are infrastructure-level features and ```vnf.``` indicates VNF-level features. Feature ```scale``` is the label created after data preprocessing.

These datasets can be directly used for training machine learning models. In our paper, we use [```StandardScaler```](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) and [```NeuralNetwork```](https://scikit-learn.org/stable/modules/neural_networks_supervised.html) from ```scikit``` to standardize feature values and generate neural network models.

## Online Data
During online stage, we use a different workload traffic to evaluate the initial neural network models. Since the scaling decisions and feature information are generated and collected in real-time, this dataset only includes the workload generation data.

We leverage an [real-world NetFlow traffic trace](https://www.simpleweb.org/wiki/index.php/Traces#NetFlow_Traces) to generate online testing workload. As the original trace is huge and spans over 8 days, we extract and average the key information such as TCP/UDP packet rate, throughput in Bps/bps, and TCP/UDP flow rate over 3600 seconds. ```envi/data/online/``` contains this information for UDP (to test Suricata) and TCP (to test Squid) traffic. Note that users may need to modulate this information (e.g., proportionally increase) to make sure the generated workload do not always overload or underload the tested VNF. In other words, the ideal testing workload should fluctuate around the system capacity point.

We also include the python scripts to extract the UDP and TCP information from the original NetFlow trace in ```envi/src/utils/```. ```wireshark-common``` and ```tshark``` are required to run the scripts.

In our paper, we use [```hing3```](https://tools.kali.org/information-gathering/hping3), [```Web Polygraph```](http://www.web-polygraph.org/), and [```Harpoon```](https://cs.colgate.edu/~jsommers/harpoon/) to generate UDP traffic, HTTP traffic, and TCP traffic respectively. Users can choose other workload generation tools as long as they follow the traffic rates in the datasets. (For UDP traffic, we use 1460 KB for packet size.)


