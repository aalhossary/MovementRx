import csv
import sys
from pathlib import Path
import numpy as np

from spmclient import consts
## Installing the library by:
# pip install samplerate
import samplerate

measurementSFX = dict([('kinematic', 'Ang'), ('moment', 'moment')])

in_folder = '../res/cases/subj1_pre'
out_folder = '../res/cases/subj1_preResampled'
infolder_mask = '{measurement}/{side}_{joint}{dimension}_{measurementSFX}_{subjname}.csv'
outfolder_mask = infolder_mask
subjname = 'subj1'


def resample_file(measurement: str, i_side: int, i_joint: int, i_dimension: int):
    side = consts.side[i_side]
    joint = consts.joint[i_joint]
    dim = consts.dim[i_dimension]
    print(measurement, side, joint, dim)
    file_name = infolder_mask\
        .replace('{measurement}', measurement).replace('{side}', side)\
        .replace('{joint}', joint).replace('{dimension}', dim)\
        .replace('{measurementSFX}', measurementSFX[measurement])\
        .replace('{subjname}', subjname)

    with open(Path(in_folder, file_name), 'r') as infile:
        reader = csv.reader(infile, delimiter=',')
        headers = next(reader)
        input_data = np.array(list(reader)).astype(np.float_)
        outpath = Path(out_folder, file_name)
        out_folder_path = outpath.parent
        if not out_folder_path.exists():
            out_folder_path.mkdir(parents=True)
        print(out_folder_path)
        with open(outpath, 'w') as outfile:
            print(', '.join(headers), file=outfile)

            converter = 'sinc_best'
            output_data = \
                input_data.transpose() if measurement != consts.MEASUREMENT_KINEMATICS \
                else samplerate.resample(input_data, 60 / 101., converter).transpose()
            print(output_data.shape)
            np.savetxt(outfile, output_data, fmt='%.9f', delimiter=',')


def main():

    for measurement in consts.measurement_folder:
        for i_side in range(len(consts.side)):
            for i_joint in range(len(consts.joint)):
                for i_dimension in range(len(consts.dim)):
                    resample_file(measurement, i_side, i_joint, i_dimension)
                    # , scales[measurement][i_joint, (i_side * 3 + i_dimension)])


if __name__ == '__main__':
    main()
