## Removing k8s cluster cleanly

1. Run `remove_cluster.sh` on every worker node
2. Run `network_restart.sh` on every worker node
3. Run `clean_network_interfaces.sh` on every worker node
4. Restart cluster and join the worker nodes to cluster
