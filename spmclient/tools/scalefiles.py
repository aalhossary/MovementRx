import csv
import sys
from pathlib import Path
import numpy as np

from spmclient import consts

measurementSFX = dict([('kinematic', 'Ang'), ('moment', 'moment')])

in_folder = '../spmclient/res/cases/Amputee'
out_folder = '../spmclient/res/cases/AmputeeFlipped'
subjname = 'subj1'  # 'subj1'
# in_folder = 'C:\\Users\\Amr\\Google Drive\\Share\\From Phillis\\amputee Apr - YZ Moment Correct\\TTA011'
# out_folder = 'C:\\Users\\Amr\\Google Drive\\Share\\From Phillis\\amputee Apr - YZ Moment Correct\\TTA011Scaled'
# subjname = 'subj1'  # 'Lam'  # 'Ref' 'subj1'
scales_file_str = './tools/KneeOAFlips.csv' #  './scales.csv'

infolder_mask = '{measurement}/{side}_{joint}{dimension}_{measurementSFX}_{subjname}.csv'
outfolder_mask = infolder_mask


def scale_file(measurement:str, i_side: int, i_joint: int, i_dimension:int, scale: float, transpose=False):
    side = consts.side[i_side]
    joint = consts.joint[i_joint]
    dim = consts.dim[i_dimension]
    print(measurement, side, joint, dim, scale)
    file_name = infolder_mask\
        .replace('{measurement}', measurement).replace('{side}', side)\
        .replace('{joint}', joint).replace('{dimension}', dim)\
        .replace('{measurementSFX}', measurementSFX[measurement])\
        .replace('{subjname}', subjname)

    with open(Path(in_folder, file_name), 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        headers = next(reader)
        headers = [l.strip() for l in headers]
        
        data = np.array(list(reader)).astype(float)

        outpath = Path(out_folder, file_name)
        out_folder_path = outpath.parent
        if not out_folder_path.exists():
            out_folder_path.mkdir(parents=True)
        print(out_folder_path)
        with open(outpath, 'w') as outfile:
            print(', '.join(headers), file=outfile)
            data = data if scale == 1 else data *scale
            if transpose:
                data = data.T
            np.savetxt(outfile, data, fmt='%.9f', delimiter=',')


def main():

    scales = dict()
    scales_path = Path(scales_file_str)
    with open(scales_path, 'r') as scales_file:
        reader = csv.reader(scales_file, delimiter=',')
        _headers = next(reader)
        data = np.array(list(reader)).astype(float)
        if data.shape != (6, 6):
            sys.exit('data not as expected')
        scales['kinematic'] = data[:3]
        scales['moment'] = data[3:]
        print(data)

    for measurement in consts.measurement_folder:

        # # This line should be REMOVED
        # transpose = (measurement == consts.measurement_folder[0])

        for i_side in range(len(consts.side)):
            for i_joint in range(len(consts.joint)):
                for i_dimension in range(len(consts.dim)):
                    scale_file(measurement, i_side, i_joint, i_dimension, 
                               scales[measurement][i_joint, (i_side * 3 + i_dimension)])  # , transpose)
    # with open()




if __name__ == '__main__':
    main()