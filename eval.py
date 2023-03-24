# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 14:33:26 2023

@author: Nádia Carvalho
"""
import pandas as pd

from src.annotations import AnnotationComparer

if __name__ == '__main__':

    annotations = pd.read_excel(
        'eval_data/annotations/form-answers.xlsx', header=[0, 1, 2], index_col=0)

    comparer = AnnotationComparer()

    media = pd.DataFrame(pd.DataFrame(annotations.iloc[[0,2]]).mean(axis=0))
    comparer.compare_annotations(media, name='Annotator-1-3')

