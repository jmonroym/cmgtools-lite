#!/usr/bin/env python
import os
import re
import sys

from runAllLimits_cp import parseNameCp  
from runAllLimits import runCombineCommand
from runSMExpectedLimits import getSMExpectedLimits

def generateToysCp(workspace, split=1, ntoys=100, seed=123456, printCommand=False,
                 queue=None):
    """
    Generate toys from a workspace without running the fit
    """
    cv,cp,tag = parseNameCp(workspace)
    if printCommand:
        print ""
        
    combinecmd =  "combine -M GenerateOnly"
    combinecmd += " -m 125 --verbose 0 -n _SMtoys_%d_cv_%s" % (ntoys, tag)
    combinecmd += " -t %d" % ntoys
    combinecmd += " --expectSignal 1"
    combinecmd += " --saveToys"
    if split > 1 and queue:
        combinecmd += " -s %d:%d:1" % (seed, seed+split-1)
    else:
        combinecmd += " -s %d" % seed
        
    if split > 1 and not queue:
        print "Ignoring split command, only works together with --queue"
        
    submitName = None if queue is None else tag
    comboutput = runCombineCommand(combinecmd, workspace, verbose=printCommand,
                                       queue=queue, submitName=submitName)

def runSMExpectedLimitsCp(card, ntoys=100, split=1, seed=123456,
                          toysfile="higgsCombine_SMtoys.GenerateOnly.mH125.123456.root",
                          queue=None,
                          printCommand=False):
    """
    Calculate observed limits on toys
    """
    cv,cp,tag = parseNameCp(card)
    if printCommand:
        print ""
        
    if queue:
        print toysfile
        
    combinecmd =  "combine -M AsymptoticLimits --run observed"
    combinecmd += " -m 125 --verbose 0 -n cv%s_SM"%tag
    combinecmd += " -t %d" % ntoys
    combinecmd += " --toysFile %s" % toysfile

    if split > 1 and queue:
        combinecmd += " -s %d:%d:1" % (seed, seed+split)
        if not r"%(SEED)s" in toysfile:
            print "Warning, need to use %%(SEED)s in toys filename!"
    else:
        combinecmd += " -s %d" % seed

    if split > 1 and not queue:
        print "Ignoring split command, only works together with --queue"
        
    comboutput = runCombineCommand(combinecmd, card,
                                   submitName=tag,
                                   queue=queue,
                                   verbose=printCommand)
    return comboutput


def main(args, options):
    cards = []
    if os.path.isdir(args[0]):
        inputdir = args[0]

        if options.tag != None:
            tag = "_"+options.tag
        elif options.tag == "":
            tag = ""
        else:
            # Try to get the tag from the input directory
            if inputdir.endswith('/'): inputdir = inputdir[:-1]
            tag = "_"+os.path.basename(inputdir)
            assert( '/' not in tag )

        cards = [os.path.join(inputdir, c) for c in os.listdir(inputdir)]

    elif os.path.exists(args[0]):
        tag = options.tag or ""
        if len(tag): tag = '_'+tag
        cards = [c for c in args if os.path.exists(c)]

    cards = [c for c in cards if any([c.endswith(ext) for ext in ['card.txt', 'card.root', '.log']])]
    cards = sorted(cards)
    print "Found %d cards to run" % len(cards)

    if options.generate:
        for n,card in enumerate(cards):
            print "...processing", card
            generateToysCp(card,
                           split=options.split,
                           ntoys=options.ntoys,
                           seed=10000+n,
                           printCommand=options.printCommand,
                           queue=options.queue)

        return 0

    if options.queue:
        # Produce the limits on the batch system
        # pair each card with a file containing N toys
        # in the directory given by options.toysfile
        # Note that we only need ONE toy file, since we want the SM
        # signal for each point.
        for card in cards:
            runSMExpectedLimitsCp(card, ntoys=options.ntoys,
                                      split=options.split,
                                      seed=10000,
                                      toysfile=options.toysfile,
                                      queue=options.queue,
                                      printCommand=options.printCommand) 
        return 0

    limdata = {} # (cv,cp) -> (2sd, 1sd, lim, 1su, 2su, [obs])
    for logfile in cards: # process the logfiles from the batch jobs
        # Recover the point first
        match = re.match(r'.*\_([\dpmc]+\_[\dpm]+)\_0_[0-9]{8}\.log', os.path.basename(logfile))
        if match == None:
            raise RuntimeError("Error parsing filename %s" % logfile)

        match = match.groups()[0]
        matchf = match.replace('p', '.').replace('m','-')

        cv,cp = tuple(map(float, matchf.split('_')))
        
        print "%-40s CV=%5.2f, Cp=%5.2f : " % (os.path.basename(logfile), cv, cp),
        with open(logfile, 'r') as output:
            limdata[(cv,cp)] = getSMExpectedLimits(output.read())


    fnames = []

    csvfname = 'limits%s_cv_%s.csv' % (tag, str(cv_).replace('.','p'))
    with open(csvfname, 'w') as csvfile:
        csvfile.write('cv,cf,twosigdown,onesigdown,exp,onesigup,twosigup\n')
        for cv,cp in sorted(limdata.keys()):
            if not cv == cv_: continue
            values = [cv, cp]
            values += [limdata[(cv,cp)][x] for x in ['twosigdown','onesigdown','exp','onesigup','twosigup']]
            if options.unblind:
                values += [limdata[(cv,cp)]['obs']]
            csvfile.write(','.join(map(str, values)) + '\n')
    print "All done. Wrote limits to: %s" % (" ".join(fnames))

    return 0

if __name__ == '__main__':
    from optparse import OptionParser
    usage = """
    %prog [options] _cp_1_.root --generate [--ntoys 100] [--split 10 --queue 8nh]
    %prog [options] _*.root [--ntoys 100] [--split 10 --queue 2nd --toysfile higgsCombine.GenerateOnly.%%(SEED)s.root]

    Generate toys from a model, possibly split into several jobs on
    lxbatch (first option).
    Then calculate limits on those toys (second option).

    Note that you need to have 'combine' in your path. Try:
    cd /afs/cern.ch/user/s/stiegerb/combine707/ ; cmsenv ; cd -
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-g","--generate", dest="generate", action='store_true',
                      help="Generate toys, then exit")
    parser.add_option("--toysfile", dest="toysfile",
                      type="string", default="toys.root",
                      help="Toys file to use")
    parser.add_option("--ntoys", dest="ntoys", type="int", default=100,
                      help="Number of toys to read")
    parser.add_option("-t","--tag", dest="tag", type="string", default=None,
                      help="Tag to put in name of output csv files")
    parser.add_option("--split", dest="split", type="int", default=1,
                      help="Split into n jobs")
    parser.add_option("-p","--printCommand", dest="printCommand", action='store_true',
                      help="Print the combine command that is run")
    parser.add_option("-q","--queue", dest="queue", type="string", default=None,
                      help="Submit jobs to this queue")
   
    (options, args) = parser.parse_args()

    sys.exit(main(args, options))
