# Specific instructions for the tHq analysis

### Add the remotes for Benjamin's repository and get the `tHq_80X_base` branch:

```
git remote add stiegerb https://github.com/stiegerb/cmgtools-lite.git -f -t tHq_80X_base
git checkout -b tHq_80X_base stiegerb/tHq_80X_base
git push -u origin tHq_80X_base
```

A current set of minitree outputs is at:
```
/afs/cern.ch/work/p/peruzzi/ra5trees/809_June9_ttH_skimOnlyMC_3ltight_relax_prescale
```
You might have to ask Marco Peruzzi for access rights to it.

----------------

### Producing mini trees

To be filled.

----------------

### Producing friend trees

Friend trees are trees containing additional information to the original trees. Each entry (i.e. event) in the original trees has a corresponding entry in the friend tree. For the tHq analysis we create friend trees with additional event variables related to forward jets, e.g. the eta of the most forward jet in each event.

The main python class calculating this information for is in the file `python/tools/tHqEventVariables.py`. The `__call__` method of that class is called once per event and returns a dictionary associating each branch name to the value for that particular event. Currently, the class only calculates and stores the highest eta of any jet with pT greater than 25 GeV (stored in a branch named "maxEtaJet25").

The class can be tested on a few events of a minitree by simply running `python tHqEventVariables.py tree.root`.

To produce the friend trees for many samples and events, a separate handler script is used, saved in `macros/prepareTHQEventVariableFriends.py`. It takes as first argument a directory with minitrees outputs, and as second argument a directory where it will store the output. To run it on a few events of a single sample, you can do this:
```
python prepareTHQEventVariableFriends.py -m tHqEventVariables -t treeProducerSusyMultilepton -N 10000 ra5trees/809_June9_ttH/ tHq_eventvars_Aug5 -d TTHnobb_mWCutfix_ext1 -c 1
```

You should use this to figure out how fast your producer is running, and adjust the chunk size (`-N` option) to have jobs of reasonable run times. Once this works, you can submit all the jobs for all samples to lxbatch, by running something like this:
```
python prepareTHQEventVariableFriends.py -m tHqEventVariables -t treeProducerSusyMultilepton -N 500000 ra5trees/809_June9_ttH/ tHq_eventvars_Aug11 -q 8nh
```

Note that the `-q` option specifies the queue to run on. The most common options would be `8nh` for jobs shorter than 8 hours, or `1nd` for jobs shorter than one day (24 hours). Keep an eye on the status of the jobs with the `bjobs` command, and look at the output of a running job with `bpeek <jobid>`. The STDOUT and STDERR log files of each job are stored in a directory named `LSFJOB_<jobid>`.

Once all the jobs have finished successfully, you can check the output files using the `friendChunkCheck.sh` script: cd to the output directory and run `friendChunkCheck.sh evVarFriend`. If there is no output from the script, all the chunks are present. To merge the junks, there is a similar script in `macros/leptons/friendChunkAdd.sh`. Run it with `. ../leptons/friendChunkAdd.sh evVarFriend`, inside the output directory.

If that went ok, you can remove all the chunk files and are left with only the friend tree files.

A first version of the trees is already produced and stored here: `/afs/cern.ch/user/s/stiegerb/work/TTHTrees/13TeV/tHq_eventvars_Aug12`.

*TODO*: add more variables like [these](https://github.com/stiegerb/cmg-cmssw/blob/thq_newjetid_for_518_samples/CMGTools/TTHAnalysis/macros/leptons/prepareTHQFriendTree.py)

----------------

### Making basic plots using `mcPlots.py`

The main script for making basic plots in the framework is in `python/plotter/mcPlots.py`, which uses the classes in `mcAnalysis.py` (for handling the samples) and `tree2yield.py` (for getting yields/histograms from the trees). It accepts three text files as inputs, one specifying the data and MC samples to be included, one listing the selection to be applied, and one configuring the variables to be plotted. Examples for these there files are in the `python/plotter/tHq-multilepton/` directory (where this README is also), with some explanation on their format in comments inside the files.

A full example for making plots with all corrections is the following:

```
python mcPlots.py \
tHq-multilepton/mca-thq-3l-mcdata-frdata.txt \
tHq-multilepton/cuts-thq-3l.txt \
tHq-multilepton/plots-thq.txt \
--s2v \
--tree treeProducerSusyMultilepton \
--showRatio --poisson \
-j 8 \
-f \
-P 809_June9_ttH_skimOnlyMC_3ltight_relax_prescale/ \
-l 12.9 \
--pdir tHq-multilepton/plots_Aug12/ \
-F sf/t tHq_eventvars_Aug12/evVarFriend_{cname}.root \
-F sf/t 809_June9_ttH_skimOnlyMC_3ltight_relax_prescale/2_recleaner_v4_b1E2/evVarFriend_{cname}.root \
--mcc ttH-multilepton/lepchoice-ttH-FO.txt \
-W 'puw2016_vtx_4fb(nVert)'
```

Note that this uses symbolic links to the `809_June9_ttH_skimOnlyMC_3ltight_relax_prescale` and `tHq_eventvars_Aug12` directories.

The important options are:

- `-P treedir/`: Input directory containing the minitree outputs
- `--pdir plotdir/`: The output directory for the plots
- `-l 12.9`: Integrated luminosity to scale the MC to (in inverse femtobarn)
- `-j 8`: Number of processes to run in parallel
- `-f`: Only apply the full set of cuts at once. Without this, it will produce sequential plots for each line in the cut file.
- `-F sf/t directory/evVarFriend_{cname}.root`: Add the tree named `sf/t` in these files as a friend
- `--mcc textfile.txt`: Read this file defining new branches as shortcuts
- `-W 'weightexpression'`: Apply this event weight

If everything goes according to play, this will produce an output directory with the plots in `.pdf` and `.png` format, a text file with the event yields, as well as a copy of the mca, cut, and plot files, the command string used, and a root file with the raw histograms.

----------------

### Some tips

- It's useful to have a symbolic link to the directory containing the minitree outputs in your working directory. E.g. like this:

```
ln -s /afs/cern.ch/work/p/peruzzi/ra5trees/809_June9_ttH
```

- Often we store the minitree files on eos, and save only a text file (`tree.root.url` in place of `tree.root`) with the location (something like `root://eoscms.cern.ch//eos/cms/store/...`). You can open them in one go like this:

```
root `cat /afs/cern.ch/user/p/peruzzi/work/ra5trees/809_June9_ttH/TTHnobb_mWCutfix_ext1/treeProducerSusyMultilepton/tree.root.url`
```
