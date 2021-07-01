# -*- coding: utf-8 -*-
import time
import traceback
from tabulate import tabulate
import utils

__all__ = ("main",)

from camelot import pdfquery_utils, faster_load


def pprint(df, return_str=False):
    try:
        pretty = tabulate(df, headers='keys', tablefmt='psql')
        if return_str:
            return pretty
        else:
            print(pretty)
    except Exception as e:
        print(traceback.format_exc())


def main():
    from camelot.io import read_pdf

    filename = "/Users/vijender/indvision-data/acctstmt_d_xxxxxx591m_emailacctstmt_unlckd.pdf"
    layouts, pq_obj, dimensions = faster_load.load_pdf_and_layout(filename, {})
    preprocess_kwargs = {
        'layouts': layouts,
        'dimensions': dimensions
    }
    # for layout in layouts[0]:
    #     print(layout.text)
    tables = read_pdf(
        filepath=filename, flavor='stream', table_areas=["0,448,605,390"], pages="1",
        row_tol=5, column_tol=0, edge_tol=100,
        num_columns=7, preprocess_kwargs=preprocess_kwargs
    )
    print(tables)
    for table in tables:
        data = table.df
        pprint(data)


if __name__ == "__main__":
    st = time.time()
    main()
    print("total time:", time.time() - st)
