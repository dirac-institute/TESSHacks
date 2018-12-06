import numpy as np
import pandas as pd
import glob

import astropy.io.fits as fits

def read_tess_info(datadir):
    """
    Traverse the directory structure of TESS light curve 
    files and get out some useful information, like 
    the TESS object ID, the subdirectory, file name 
    and cadence.
    
    Parameters
    ----------
    datadir: str
        The path to the top level directory where the 
        TESS data is located.
        
    Returns
    -------
    tess_info : pd.DataFrame
        A DataFrame with some useful information about the 
        TESS light curves.
        Columns:
            * subdir: the sub-directory where the file is located
            * filename: the actual file name of the data file
            * daterange: the date range of the data, taken from the file name
            * sector_no : the sector number, taken from the file name
            * tess_id: the Tess Object Identifier, taken from the file name
            * cadence: the cadence of the light curve, taken from the file name
    """
    # glob all the data files
    datafiles = glob.glob(datadir+"**/*.fits", recursive=True)
    
    tess_info = []

    # loop over all data files
    for f in datafiles:
        # make an empty dictionary for the information
        single_info = {}

        # split the path into folders
        fsplit = f.split("/")
        # get out the sub-directory with the file
        single_info["subdir"] = fsplit[-2]

        # get the filename
        single_info["filename"] = fsplit[-1]

        # split the filename
        fname_split = single_info["filename"].split("-")

        # split out information in the filename
        single_info["daterange"] = fname_split[0]
        single_info["sector_no"] = fname_split[1]
        single_info["tess_id"] = np.int(fname_split[2])
        single_info["cadence"] = fname_split[3]

        # append to list
        tess_info.append(single_info)
        
    # make a data frame
    tess_info = pd.DataFrame(tess_info)

    return tess_info

def crossmatch_gaia(tess_info, gaia_files):
    """
    Compute a cross-matched table with the GAIA information.

    Parameters
    ----------
    tess_info: pd.DataFrame
       A data frame e.g. as made by `read_tess_info` above.

    gaia_files: list of str
       A list of paths to CSV files that cross-match Gaia on the 
       TESS object IDs. The relevant column in those files with the 
       TIC must be called `ticid`, in `tess_info` must be called `tess_id`

    Return
    ------
    tess_gaia : pd.DataFrame
       Merged data frame.
    """

   gaiamatch = []
   for gf in gaia_files:
       gm = pd.read_csv(gf)
       gaiamatch.append(gm)

   # concatenate all the individual cross-matches
   gaia_merged = pd.concat(gaiamatch, ignore_index=True, sort=True)
   
   # merge the TESS and Gaia data frames
   tess_gaia = pd.merge(tess_info, gaiamatch, left_on="tess_id", right_on="ticid")

   return tess_gaia
   
