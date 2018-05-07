#!/usr/bin/env python
import os
import re
import sys
import numpy as np
from math import floor, ceil
#from limitStatsFromCombineLogs import calculateMeanMedInterval

def getLimitValsCp(logfile):
    values = []
    kappa_p = None
 
    match = re.match(r'job\_tHq\_cp\_([\dpmc]+)\_([\d])+\_[\d]*\.log', logfile)
    cp = match.group(1)
    kappa_p= float(cp.replace('p','.').replace('m','-'))

    with open(logfile, "r") as lfile:
        for line in lfile:
            if line.startswith("Observed Limit:"):
                limitval = float(line.split("r < ")[1])
                values.append(limitval)

    if cp is None: 
        print "failed to determine kappa_p for", logfile

    return values, kappa_p


def calculateMeanMedIntervals(values):
    values = sorted(values)
    mean, median = np.mean(values), np.median(values)

    hi68 = values[min(len(values) - 1, int(ceil(0.84 * len(values))))]
    lo68 = values[min(len(values) - 1, int(floor(0.16 * len(values))))]
    hi95 = values[min(len(values) - 1, int(ceil(0.975 * len(values))))]
    lo95 = values[min(len(values) - 1, int(floor(0.025 * len(values))))]

    print "mean %.4f, median %.4f" % (mean, median),
    print "(%.4f (%.4f < r < %.4f ) %.4f)" % (lo95, lo68, hi68, hi95)

    return mean, median, lo68, hi68, lo95, hi95

if __name__ == '__main__':
    """
    Usage: limitStatsFromCombineLogs.py *.log

    Gather statistics from combine output logs (when submitting to batch).
    Looks for lines with 'Observed Limit:' and collects the values. Attempts
    to determine kappa_t and kappa_V from the log file. Then store those limit
    values grouped by kappa_t/kappa_V and calculate mean, median, and 68%/95%
    bands.
    Saves the result in a combineLogStats.csv file
    """
    data = {}
    nfiles = 0
    for filename in sys.argv[1:]:
        if not (os.path.isfile(filename) and filename.endswith('.log')):
            print "... ignoring", filename
            continue

        values, kappa_p = getLimitValsCp(filename)
        if len(values) < 100:
            print "WARNING, found only %d limits in %s" % (len(values), filename)

        nfiles += 1

        basename = os.path.basename(filename)
        match = re.match(r'job\_tHq\_cp\_([\dpm]+)\_([\d])+\_[\d]*\.log', basename)
        if not match:
            print "WARNING, couldn't match filename to pattern"
            tag = None
        else:
            tag = match.group(1)

        data.setdefault(kappa_p, {})[tag] = values

    # Add up the split toy results
    aggdata = {}
    for kappa_p, splitvalues in data.items():
        for values in splitvalues.values():
            aggdata.setdefault(kappa_p, []).extend(values)

    print "Processed %d log files for %d different kp values" % (nfiles, len(data.keys()))

    csvfilename = 'combineLogStats_cp.csv'
    assert(not os.path.isfile(csvfilename)), 'file exists: %s' % csvfilename
    with open(csvfilename, 'w') as csvfile:
        csvfile.write('cp,twosigdown,onesigdown,exp,onesigup,twosigup,ntoys\n')

        for kappa_p, values in sorted(aggdata.items()):

            #print kappa_p

            print " %4d toys for %+.3f" % (len(values), kappa_p),
            mean,median,lo68,hi68,lo95,hi95 = calculateMeanMedIntervals(values)
            csvfile.write(','.join(map(str, [kappa_p,lo95,lo68,median,hi68,hi95,len(values)])))
            csvfile.write('\n')
