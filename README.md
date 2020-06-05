# minKNOWER
Python Oxford Nanopore MinKnow API wrapper

## Setup
```

git clone https://github.com/thequicksort/minknowapi.git;
pushd minknowapi;
bash ./bootstrap_dev.sh
```
Now you have all the dependencies and are ready to run.
The next steps assume MinKnow and nanopore device are attached to your local machine. 
Totally okay if not, just set the environment variable `MY_IP_ADDRESS` to the corresponding machine's IP address (e.g. `MY_IP_ADDRESS="My.Remote.Machine.IP"`)
instead of running `MY_IP_ADDRESS=$(ipconfig getifaddr en0)`

## Run the demo
```
nix-shell ./nix/shell.nix
MY_IP_ADDRESS=$(ipconfig getifaddr en0)
python ./examples/live_data_graph.py --ip=$MY_IP_ADDRESS
```
