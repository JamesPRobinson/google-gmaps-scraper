from pathlib import Path
import os

path = Path('config.py')
RES_FOLDER = path.parent.parent.joinpath('results')
MODULE_FOLDER = path.parent
ROOT_FOLDER = MODULE_FOLDER.parent
