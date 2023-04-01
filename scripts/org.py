import os
import glob

# if __name__ == '__main__':
#     ext = 'xml'

#     for f in glob.glob(f'eval_data/MTCFeatures/reductions/**/*.{ext}', recursive=True):
#         splitted = f.split(os.sep)
#         fold = os.path.join(*splitted[:-1] + [f'{ext.upper()}s'])

#         os.makedirs(fold, exist_ok=True)
#         os.rename(f, os.path.join([fold, splitted[-1]])) # type: ignore
