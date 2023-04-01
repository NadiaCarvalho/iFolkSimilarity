# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 14:33:26 2023

@author: Nádia Carvalho
"""
from itertools import combinations

import pandas as pd

from src.annotations import AnnotationComparer

if __name__ == '__main__':

    annotations = pd.read_excel(
        'eval_data/annotations/form-answers.xlsx', header=[0, 1, 2], index_col=0)

    comparer = AnnotationComparer()

    # for r in range(1, 4):
    #     for p in combinations(range(1,4), r):
    #         if r == 1:
    #             comparer.compare_annotations(pd.DataFrame(annotations.iloc[p[0]-1]), name=f'Annotator-{p[0]}')
    #         else:
    #             media = pd.DataFrame(pd.DataFrame(annotations.iloc[[px-1 for px in p]]).mean(axis=0))
    #             comparer.compare_annotations(media, name=f"Annotator-{'-'.join([str(i) for i in p])}")

    for r in range(1, 4):
        for p in combinations(range(1,4), r):
            comparer.create_comparison_graphs(f'eval_data/annotations/Annotator-{"-".join([str(i) for i in p])}/pearson.xlsx')
            comparer.create_comparison_graphs(f'eval_data/annotations/Annotator-{"-".join([str(i) for i in p])}/rsquare.xlsx')

