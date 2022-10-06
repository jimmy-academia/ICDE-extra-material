# Experiment Code for ICDE submission #640

> Quick Notes: the repository includes the demographic files (`demo/epinions.pt, demo/ciao.pt`)

## Usage

1. download and process data 
```bash!
bash data/get_data.sh
bash data/prepare_data.sh
```
2. prepare demographics (will replace existing files)
```bash!
python build_demographic.py
```
> builds in `demo/[dataset].pt`

3. run experiments

* train normal recsys (not poisoned): `python recsys.py`
> save in `cache/model_weights/[dataset_modeltype].pth`

* run all experiments sequentially
```bash!
# The experiments for Table III
bash scripts/all_2p.sh -d ciao -a -g <device>
bash scripts/all_2p.sh -d ciao -m -g <device>
bash scripts/all_2p.sh -d epinions -a -g <device>
bash scripts/all_2p.sh -d epinions -m -g <device>

# The experiments for Fig. 2 
## NOTE: should be conducted after finishing all_2p experiments for the first opponent poison.
bash scripts/all_num.sh -d ciao -g <device>
bash scripts/all_num.sh -d ciao -m -g <device>
bash scripts/all_num.sh -d epinions -g <device>
bash scripts/all_num.sh -d epinions -m -g <device>

# The experiments for Fig. 4
bash scripts/all_opb.sh -d ciao -g <device>
bash scripts/all_opb.sh -d ciao -m -g <device>
bash scripts/all_opb.sh -d epinions -g <device>
bash scripts/all_opb.sh -d epinions -m -g <device>

```

* run individual experiment
```bash!
python main.py 
    --dataset [ciao/epinions] 
    --nop [0,1,2..] 
    --task [mca/ca/ia/none/pga/trial/rev/srwa]
    --method [msops/bops/popular/random]
```

> Note: msops, bops is earlier namings for msopds, bopds.


4. aggregate result
```bash!
python print_tables.py
python quick_fetch_figures.py
```
