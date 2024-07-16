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
import sncosmo
import gzip
from io import StringIO
from contextlib import contextmanager

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
                    print(lc_file)
                    lc_raw = fh.read().decode("utf-8")
                    lc_fh  = StringIO(lc_raw)
                    meta, lc_dat
                    a = sncosmo.read_snana_ascii(lc_fh, default_tablename='OBS')

                    # give up if we don't load any data
                    if not 'OBS' in lc_data.keys():
                        continue

                    print(lc_data['OBS'])





if __name__=='__main__':
    sys.exit(main())
