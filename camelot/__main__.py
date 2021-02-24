# -*- coding: utf-8 -*-
import traceback
from tabulate import tabulate

__all__ = ("main",)


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
    tables = read_pdf(
        "/Users/vijender/indvision-data/2020_11_0319_33_38_008446_1604432018_unlckd_reptd_redacted_merged.pdf",
        flavor='stream', table_areas=["0,1910,595,1860"])
    tables.export('foo.csv', f='csv', compress=False)
    data = tables[0].df
    pprint(data)


if __name__ == "__main__":
    main()
