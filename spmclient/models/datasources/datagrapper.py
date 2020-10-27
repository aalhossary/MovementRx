from pathlib import Path
from re import compile
from typing import Dict, Union

import numpy as np
from spmclient import consts


commonPattern = f'({consts.side[0]}|{consts.side[1]})_'\
                f'({consts.joint[0]}|{consts.joint[1]}|{consts.joint[2]})'\
                f'({consts.dim[0]}|{consts.dim[1]}|{consts.dim[2]})_'
kinematic_filename_mask = compile(commonPattern + f'({consts.measurement_suffix[0]})_(.+)\\.csv')
moment_filename_mask = compile(commonPattern + f'({consts.measurement_suffix[1]})_(.+)\\.csv')
any_filename_mask = compile(commonPattern + f'({consts.measurement_suffix[0]}|{consts.measurement_suffix[1]})_(.+)\\.csv')


def load_file(file: Path) -> np.ndarray:
    data = np.genfromtxt(file, dtype=float, delimiter=',', skip_header=1)
    return data


def load_full_folder(root_path: Union[Path, str], scale=False) -> Dict:
    """Return the data in the order (Measurement, subject (person), side, joint, dimension"""
    # print('starting to load full folder')
    ret_dict = dict()
    if isinstance(root_path, str):
        root_path = Path(root_path)
    for _, measurment in enumerate(consts.measurement_folder):
        folder = root_path / measurment
        if folder.exists():
            print('folder exists')
            generator = folder.iterdir()  # glob(str(kinematic_filename_mask))
            for f in generator:
                matched = any_filename_mask.fullmatch(f.name)
                # print(matched)
                s = matched.group(1)
                j = matched.group(2)
                dim = matched.group(3)
                msrmnt_sfx = matched.group(4)
                subj = matched.group(5)
                print(s, j, dim, msrmnt_sfx, subj)

                measurement_dict = ret_dict.setdefault(measurment, dict())
                subject_dict = measurement_dict.setdefault(subj, dict())
                side_dict = subject_dict.setdefault(s, dict())
                joint_dict = side_dict.setdefault(j, dict())
                temp_data = load_file(f)
                
#                 # -------- test start------------------
#                 if scale and measurment == consts.MEASUREMENT_MOMENTS:
#                     temp_data *= 16.5
#                 # -------- test end ------------------

#                 #  TODO FIXME This condition should be replaced with a permanent data format
#                 if len(temp_data):
#                     shape = temp_data.shape
#                     if shape[1] < 50:
#                         temp_data = temp_data.transpose()
                
                joint_dict[dim] = temp_data

    return ret_dict
