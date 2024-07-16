#!/usr/bin/env python
'''
Simple script to process lcmerge data in SNDATA_ROOT and impose tight quality cuts
in advance of modeling with a Gaussian Process
Gautham Narayan
20240716
'''
import sys
import os
import glob
import shutil
import numpy as np
import sncosmo
import gzip
from io import StringIO
from contextlib import contextmanager
from collections import Counter

def get_files_from_lcmerge_dir(data_dir):
    '''
    Returns a list of files from a SNANA SNDATA_ROOT
    '''
    lc_files = glob.glob(os.path.join(data_dir, '*DAT*'))
    out_files = []
    for lc_file in lc_files:
        if os.path.isdir(lc_file):
            # recursive call
            out_files.extend(get_files_from_lcmerge_dir(lc_file))
        elif os.path.isfile(lc_file):
            out_files.append(lc_file)
        else:
            print(f"Huh ${lc_file}")
            continue
    return(out_files)


@contextmanager
def safe_open_lc_file_gzip(lc_file, mode="rb"):
    try:
        fh = gzip.open(lc_file, mode)
    except Exception as err:
        yield None, err
    else:
        try:
            yield fh, None
        finally:
            fh.close()



def main():
    '''
    Read the LC files in the lcmerge directory of SNDATA ROOT
    Do some quality cuts and select the "best" objects
    Make some plots of LC + GP model  for the LC
    '''

    # SNDATA_ROOT has many subdirs inside lcmerge for different papers/suveys
    # we don't need/want all of them
    SNDATA_ROOT = os.getenv('SNDATA_ROOT')
    lcmerge = os.path.join(SNDATA_ROOT, 'lcmerge')
    data_dirs = glob.glob(os.path.join(lcmerge, '*'))
    use_surveys = ['CSPDR3', 'DES-SN5YR', 'CFA3_KEPLERCAM', 'CFA4', 'Pantheon+', 'SNLS3year', 'SDSS_HOLTZ08']

    outdir = os.path.join(os.getcwd(), 'training_set')
    plotdir = os.path.join(outdir, 'plots')
    os.makedirs(plotdir, exist_ok=True)

    for data_dir in data_dirs:
        survey_dir = os.path.basename(data_dir)

        # Skip surveys that aren't in the good list, where good list is determined by GN diktat
        if survey_dir not in use_surveys:
            continue

        lc_files = get_files_from_lcmerge_dir(data_dir)
        for lc_file in lc_files:

            if not lc_file.lower().endswith('dat.gz'):
                continue

            # GN - 20240716 - some of the lcmerge files don't have their data in an 'OBS' table
            # that's probably not good - it seems like mostly SNLS3yr
            with safe_open_lc_file_gzip(lc_file) as (fh, err):
                if err:
                    print(f"IOError ${lcfile}")
                    continue
                else:
                    lc_raw = fh.read().decode("utf-8")
                    lc_fh  = StringIO(lc_raw)
                    meta, lc_data = sncosmo.read_snana_ascii(lc_fh, default_tablename='OBS')

                    # give up if we don't load any data
                    if not 'OBS' in lc_data.keys():
                        continue

                    # give up if there is nothing like a PEAKMJD guess
                    # this may cost some good data, but more likely SN without this
                    # don't have good phase coverage around peak
                    if (not ('PEAKMJD' in meta)) and (not ('SEARCH_PEAKMJD' in meta)):
                        continue

                    flt = lc_data['OBS']['FLT']
                    flt_counts = Counter(flt)

                    # quality cuts
                    # demand at least 30 points on the light curve
                    if flt_counts.total() < 30:
                        continue
                    # demand at least three filters
                    if len(list(flt_counts)) < 3:
                        continue

                    # require at least 15 points with SNR > 5 (any filter)
                    fluxcal = lc_data['OBS']['FLUXCAL']
                    fluxcalerr  = lc_data['OBS']['FLUXCALERR']
                    snr = fluxcal/fluxcalerr
                    if np.count_nonzero(snr > 5) < 15:
                        continue

                    # require 5 points before peak (any filter) and 10 after (any filter)
                    peakmjd = meta.get('PEAKMJD', meta.get('SEARCH_PEAKMJD'))
                    mjd = lc_data['OBS']['MJD']
                    if np.count_nonzero(mjd <= peakmjd) < 5:
                        continue
                    if np.count_nonzero(mjd > peakmjd) < 10:
                        continue

                    #plottable = lc_data['OBS'].copy()
                    #plottable['zpt'] = np.repeat(27.5, len(plottable))
                    #plottable['zpsys'] = np.repeat('fake', len(plottable))
                    #plottable.rename_column('FLUXCAL', 'flux')
                    #plottable.rename_column('FLUXCALERR', 'fluxerr')
                    #basefile = os.path.basename(lc_file)
                    #outfile = os.path.join(outdir, basefile)
                    #shutil.copyfile(lc_file, outfile)
                    #plotfile = os.path.join(plotdir, basefile.rstrip('.gz')+'.pdf')
                    #sncosmo.plot_lc(plottable, fname=plotfile, format='pdf')

                    print(os.path.basename(lc_file), flt_counts)



if __name__=='__main__':
    sys.exit(main())
