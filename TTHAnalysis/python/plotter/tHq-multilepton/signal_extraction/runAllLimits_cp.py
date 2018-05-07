#!/usr/bin/env python
import sys, os, re, shlex
from subprocess import Popen, PIPE
from runAllLimits import runCombineCommand

def parseNameCp(card, printout=True):
    # Turn the tag into floats:
    print card
    
    tag = re.match(r'.*\_([\dpmc]+\_[\dpm]+).*\.card\.(txt|root)', os.path.basename(card))
    if tag == None:
        print "Couldn't figure out this one: %s" % card
        return

    tag = tag.groups()[0]
    tagf = tag.replace('cp','1')
    tagf = tagf.replace('p', '.').replace('m','-')
        
    cv,cp = tuple(map(float, tagf.split('_')))
    if printout:
        print "%-40s CV=%5.2f, Cp=%5.2f : " % (os.path.basename(card), cv, cp),
    return cv, cp, tag

def getLimitsCp(card, unblind=False, printCommand=False):
    """
    Run combine on a single card, return a tuple of 
    (cv,cp,twosigdown,onesigdown,exp,onesigup,twosigup)
    """
    cv,cp,tag = parseNameCp(card, True) 
    if printCommand: print ""

    combinecmd =  "combine -M AsymptoticLimits"
    if not unblind:
        combinecmd += " --run blind"
    combinecmd += " -m 125 --verbose 0 -n cvcp%s"%tag
    
    comboutput = runCombineCommand(combinecmd, card, verbose=printCommand)

    liminfo = {}
    for line in comboutput.split('\n'):
        if line.startswith('Observed Limit:'):
            liminfo['obs'] = float(line.rsplit('<', 1)[1].strip())
        if line.startswith('Expected'):
            value = float(line.rsplit('<', 1)[1].strip())
            if   'Expected  2.5%' in line: liminfo['twosigdown'] = value
            elif 'Expected 16.0%' in line: liminfo['onesigdown'] = value
            elif 'Expected 50.0%' in line: liminfo['exp']        = value
            elif 'Expected 84.0%' in line: liminfo['onesigup']   = value
            elif 'Expected 97.5%' in line: liminfo['twosigup']   = value

    print "%5.2f, %5.2f, \033[92m%5.2f\033[0m, %5.2f, %5.2f" %(
        liminfo['twosigdown'], liminfo['onesigdown'], liminfo['exp'],
        liminfo['onesigup'], liminfo['twosigup']),
    if 'obs' in liminfo: # Add observed limit to output, in case it's there
        print "\033[1m %5.2f \033[0m" % (liminfo['obs'])
    else:
        print ""
    return cv, cp, liminfo

def getFitValuesCp(card, unblind=False, printCommand=False):
    """
    Run combine on a single card, return a tuple of fitvalues
    (cv,cp,median,downerror,uperror)
    """
    cv,cp,tag = parseNameCp(card)
    if printCommand: print ""

    combinecmd =  "combine -M MaxLikelihoodFit"
    combinecmd += " -m 125 --verbose 0 -n cvct%s"%tag

    comboutput = runCombineCommand(combinecmd, card, verbose=printCommand)

    fitinfo = {}
    for line in comboutput.split('\n'):
        if line.startswith('Best'):
            fitinfo['median'] = float((line.split(': ')[1]).split('  ')[0])
            fitinfo['downerror'] = float((line.split('  ')[1]).split('/')[0])
            fitinfo['uperror'] = float((line.split('+')[1]).split('  (')[0])

    print "\033[92m%5.2f\033[0m, %5.2f, %5.2f" %( fitinfo['median'], fitinfo['downerror'], fitinfo['uperror'])
    return cv, cp, fitinfo

def getSignificanceCp(card, unblind=False, printCommand=False):
    """
    Run combine on a single card, return significance
    """
    cv,cp,tag = parseNameCp(card)
    if printCommand: print ""

    combinecmd =  "combine -M ProfileLikelihood --signif"
    combinecmd += " -m 125 --verbose 0 -n cvct%s"%tag
    comboutput = runCombineCommand(combinecmd, card, verbose=printCommand)

    significance = {}
    for line in comboutput.split('\n'):
        if line.startswith('Significance'):
            print(line)
            significance['value'] = float(line.rsplit(':', 1)[1].strip())

    print "\033[92m%5.2f\033[0m" %( significance['value'])
    return cv, cp, significance

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

    if options.runmode.lower() == 'limits':
        limdata = {} # (cv,cp) -> (2sd, 1sd, lim, 1su, 2su, [obs])
        for card in cards:

            cv, cp, liminfo = getLimits(card, model=options.model,
                                        unblind=options.unblind,
                                        printCommand=options.printCommand)
            limdata[(cv,cp)] = liminfo
    
        fnames = []
        csvfname = 'limits%s_cv_%s.csv' % (tag, str(cv_).replace('.','p'))
        with open(csvfname, 'w') as csvfile:
            if options.unblind:
                csvfile.write('cv,cp,twosigdown,onesigdown,exp,onesigup,twosigup,obs\n')
            else:
                csvfile.write('cv,cp,twosigdown,onesigdown,exp,onesigup,twosigup\n')
            for cv,cp in sorted(limdata.keys()):
                if not cv == cv_: continue
                values = [cv, cp]
                values += [limdata[(cv,cp)][x] for x in ['twosigdown','onesigdown','exp','onesigup','twosigup']]
                if options.unblind:
                    values += [limdata[(cv,cp)]['obs']]
                csvfile.write(','.join(map(str, values)) + '\n')
        
        print "All done. Wrote limits to: %s" % (" ".join(fnames))

    if options.runmode.lower() == 'fit':
        fitdata = {} # (cv,cp) -> (fit, down, up)
        for card in cards:
            cv, cp, fitinfo = getFitValuesCp(card, unblind=options.unblind,
                                             printCommand=options.printCommand)
            fitdata[(cv,cp)] = fitinfo

        fnames = []
        csvfname = 'fits%s_cv_%s.csv' % (tag, str(cv_).replace('.','p'))
        with open(csvfname, 'w') as csvfile:
            if options.unblind:
                csvfile.write('cv,cf,median,downerror,uperror\n')
            else:
                csvfile.write('cv,cf,median,downerror,uperror\n')
            for cv,cp in sorted(fitdata.keys()):
                if not cv == cv_: continue
                values = [cv, cp]
                values += [fitdata[(cv,cp)][x] for x in ['median','downerror','uperror']]
                csvfile.write(','.join(map(str, values)) + '\n')
           
        print "Wrote limits to: %s" % (" ".join(fnames))

    if options.runmode.lower() == 'sig':
        sigdata = {}
        for card in cards:
            cv, cp, significance = getSignificanceCp(card, unblind=options.unblind,
                                                     printCommand=options.printCommand)
            sigdata[(cv,cp)] = significance

        fnames = []
        csvfname = 'significance%s_cv_%s.csv' % (tag, str(cv_).replace('.','p'))
        with open(csvfname, 'w') as csvfile:
            csvfile.write('cv,cf,significance\n')
            for cv,ct in sorted(sigdata.keys()):
                if not cv == cv_: continue
                values = [cv, cp]
                values += [sigdata[(cv,cp)][x] for x in ['value']]
                csvfile.write(','.join(map(str, values)) + '\n')

        print "Wrote significance to: %s" % (" ".join(fnames))

    return 0

if __name__ == '__main__':
    from optparse import OptionParser
    usage = """
    %prog [options] dir/]

    Call combine on all datacards ("*.card.txt") in an input directory.
    Collect the limit, 1, and 2 sigma bands from the output, and store
    them together with the cv and ct values (extracted from the filename)
    in a .csv file.

    Note that you need to have 'combine' in your path. Try:
    cd /afs/cern.ch/user/s/stiegerb/combine/ ; cmsenv ; cd -
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-r","--run", dest="runmode", type="string", default="limits",
                      help="What to run (limits|fit|sig|sig)")
    parser.add_option("-t","--tag", dest="tag", type="string", default=None,
                      help="Tag to put in name of output csv files")
    parser.add_option("-u","--unblind", dest="unblind", action='store_true',
                      help="For limits mode: add the observed limit")
    parser.add_option("-p","--printCommand", dest="printCommand", action='store_true',
                      help="Print the combine command that is run")

    (options, args) = parser.parse_args()

    sys.exit(main(args, options))