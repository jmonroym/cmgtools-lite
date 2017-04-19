#!/usr/bin/env python
import os

import re
import ROOT
from CMGTools.TTHAnalysis.plotter.tree2yield import CutsFile
from optparse import OptionParser

parser = OptionParser(usage="usage: %prog [options] rootfile \nrun with --help to get list of options")
parser.add_option("-r"    , "--run-range"  , dest="runrange"    , default=(0          , 99999999)                  , type="float"                             , nargs=2                           , help="Run range")
parser.add_option("-c"    , "--cut-file"   , dest="cutfile"     , default=None        , type="string"              , help="Cut file to apply")
parser.add_option("-C"    , "--cut"        , dest="cut"         , default=None        , type="string"              , help="Cut to apply")
parser.add_option("-T"    , "--type"       , dest="type"        , default=None        , type="string"              , help="Type of events to select")
# parser.add_option("-F"  , "--fudge"      , dest="fudge"       , default=False       , action="store_true"        , help="print -999 for missing variables")
#parser.add_option("-F"  , "--add-friend" , dest="friendTrees" , action="append"     , default=[]                 , nargs=2                                  , help="Add a friend tree (treename , filename). Can use {name} , {cname} patterns in the treename")

#######

parser.add_option("-F"    , "--friendDir"  , dest="friendDir"   , type="string"       , default=["thqtrees/tHq_production_Jan25/1_thq_recleaner_240217/","thqtrees/tHq_production_Jan25/2_thq_friends_Feb24/","thqtrees/tHq_production_Jan25/5_triggerDecision_250117_v1/","thqtrees/tHq_production_Jan25/6_bTagSF_v2/"], help="Look for friends in this dir")

######

parser.add_option("-t"    , "--treeDir"    , dest="treeDir"     , type="string"       , default="thqtrees/TREES_TTH_250117_Summer16_JECV3_noClean_qgV2_tHqsoup_v2/" , help="Look for trees in this dir")
parser.add_option("-m"    , "--mc"         , dest="ismc"        , default=False       , action="store_true"        , help="print MC match info")
parser.add_option("--mm"  , "--more-mc"    , dest="moremc"      , default=False       , action="store_true"        , help="print more MC match info")
parser.add_option("--tau" , dest="tau"     , default=False      , action="store_true" , help="print Taus")
parser.add_option("-j"    , "--json"       , dest="json"        , default=None        , type="string"              , help="JSON file to apply")
parser.add_option("-n"    , "--maxEvents"  , dest="maxEvents"   , default=-1          , type="int"                 , help="Max events")
parser.add_option("-f"    , "--format"     , dest="fmt"         , default=None        , type="string"              , help="Print this format string")

parser.add_option("--outFile", dest="outFile", default="eventList.txt", type="string", help="Dump the event list to this file")

### CUT-file options
parser.add_option("-S", "--start-at-cut",dest="startCut",   type="string", help="Run selection starting at the cut matched by this regexp, included.")
parser.add_option("-U", "--up-to-cut",   dest="upToCut",   type="string", help="Run selection only up to the cut matched by this regexp, included.")
parser.add_option("-X", "--exclude-cut", dest="cutsToExclude", action="append", default=[], help="Cuts to exclude (regexp matching cut name), can specify multiple times.")
parser.add_option("-I", "--invert-cut",  dest="cutsToInvert",  action="append", default=[], help="Cuts to invert (regexp matching cut name), can specify multiple times.")
parser.add_option("-R", "--replace-cut", dest="cutsToReplace", action="append", default=[], nargs=3, help="Cuts to invert (regexp of old cut name, new name, new cut); can specify multiple times.")
parser.add_option("-A", "--add-cut",     dest="cutsToAdd",     action="append", default=[], nargs=3, help="Cuts to insert (regexp of cut name after which this cut should go, new name, new cut); can specify multiple times.")

(options, args) = parser.parse_args()

if options.cut and options.cutfile: raise RuntimeError, "You can't specify both a cut and a cutfile"

if "/functions_cc.so" not in ROOT.gSystem.GetLibraries():
    ROOT.gROOT.ProcessLine(".L %s/src/CMGTools/TTHAnalysis/python/plotter/functions.cc+"
                            % os.environ['CMSSW_BASE']);

cut = None
if options.cutfile:
    #cut = CutsFile(options.cutfile,options).allCuts()
    cut = CutsFile(options.cutfile, options=None, ignoreEmptyOptionsEnforcement=True).allCuts()
    print "Processing %s" % options.cutfile
elif options.cut:
    cut = options.cut
    print "Processing %s" % cut

with open(options.outFile, "w") as outputfile:
    for procname in args[0].split(','):
        filename = os.path.join(options.treeDir, procname,"treeProducerSusyMultilepton","tree.root")
        file = ROOT.TFile.Open(filename)
        treename = "tree"
        tree = file.Get(treename)

        #########
        for frienddir in options.friendDir:
            fname = os.path.join(frienddir, "evVarFriend_%s.root"%procname)
            tf = tree.AddFriend("sf/t", fname),
            print "added friend tree from ", frienddir
        ###############

        tree.Draw(">>elist",cut)
        elist = ROOT.gDirectory.Get("elist")
        tree.SetEventList(elist)
        tree.SetScanField(0) ## scan ALL rows

        tree.GetPlayer().SetScanRedirect(True)
        tempfilename = ".treescan_temp_%s.txt" % procname
        tree.GetPlayer().SetScanFileName(tempfilename)
        # tree.Scan("evt","","colsize=10")
        branches = ["run", "lumi", "evt",
                   # "nJet25_Recl", "nBJetMedium25_Recl",
                   # "JetSel_Recl_btagCSV[0]", "JetSel_Recl_btagCSV[1]",
                   # "JetSel_Recl_pt[0]", "JetSel_Recl_pt[1]",
                   # "LepGood_mvaTTH[iLepFO_Recl[0]]","LepGood_mvaTTH[iLepFO_Recl[1]]","LepGood_mvaTTH[iLepFO_Recl[2]]",
                    ]
        tree.Scan(":".join(branches),"","colsize=11")

        print "... %d events selected in %s" % (tree.GetEntries(cut), procname)

        with open(tempfilename, "r") as tempfile:
            if outputfile.tell() == 0:
                # Write the branch names the first time we write anything
                outputfile.write('#'+ ','.join(branches) + '\n') 
            # outputfile.write("## %s \n" % procname)
            for line in tempfile:
                spline = line.split('*')
                spline = [v for v in spline if len(v) and not v == '\n'] # clean empty entries
                if len(spline) < 2 or 'Row' in spline[0]: continue
                try:
                    # eventno = int(spline[2].strip())
                    outputfile.write(','.join([s.strip() for s in spline[1:]]))
                    outputfile.write('\n')
                except ValueError:
                    continue

        os.system('rm %s' % tempfilename)


    # print 'hello', len(output)

chan = re.split("List_","%s"%options.cutfile)[-1]
os.rename('eventList.txt','eventList_%s_%s'%(procname, chan))
