## Processing load experiment

1. The notebook name with `{function_name}_experiments.ipynb` processes the workload for that function and plots the graphs in the same notebook. It should be run in a folder that contains folders created by the `run_workload/openwhisk/execute_load_exp.sh` that contains the raw information from the invoked workload.
2. The notebook name with `{function_name}_processing.ipynb` is the same as `{function_name}_experiments.ipynb` but differs in by not plotting the graphs but insteading exporting the results as a json file. These notebooks are used to create the evaluation data in the data folder.
3. The `wasm_only` directory contains load experiments only on Spin.