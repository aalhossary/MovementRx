from pathlib import Path
from typing import Dict, Union
from re import Pattern, compile

import numpy as np

from src import consts

commonPattern = f'({consts.side[0]}|{consts.side[1]})_'\
                f'({consts.joint[0]}|{consts.joint[1]}|{consts.joint[2]})'\
                f'({consts.dim[0]}|{consts.dim[1]}|{consts.dim[2]})_'
kinematic_filename_mask = compile(commonPattern + f'({consts.measurement_suffix[0]})_(.+)\\.csv')
moment_filename_mask = compile(commonPattern + f'({consts.measurement_suffix[1]})_(.+)\\.csv')
any_filename_mask = compile(commonPattern + f'({consts.measurement_suffix[0]}|{consts.measurement_suffix[1]})_(.+)\\.csv')


def load_file(file: Path) -> np.ndarray:
    data = np.genfromtxt(file, dtype=float, delimiter=',', skip_header=1)
    return data


def load_full_folder(root_path: Union[Path, str]) -> Dict:
    """Return the data in the order (Measurement, subject (person), side, joint, dimension"""
    # print('starting to load full folder')
    ret_dict = dict()
    if isinstance(root_path, str):
        root_path = Path(root_path)
    for i, measurment in enumerate(consts.measurement_folder):
        folder = root_path / measurment
        if folder.exists():
            print('folder exists')
            generator = folder.iterdir()  # glob(str(kinematic_filename_mask))
            for f in generator:
                # print(f)
                # s = ret_dict.setdefault(measurment, dict())
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
                joint_dict[dim] = load_file(f)

    return ret_dict

