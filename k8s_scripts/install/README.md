## Helper K8s scripts

This directory contains scripts for installing the prerequisites and setting up K8s cluster before deploying OpenWhisk.

1. Run `installation_script.sh` to install containerd, helm, and K8s.
2. Setup master node using `start_cluster.sh`.
3. Join worker nodes by running the command in cluster_token.txt.
4. Label worker nodes using `label_workers.sh`.
5. Label openwhisk nodes using `label_ow_nodes.sh`.  

