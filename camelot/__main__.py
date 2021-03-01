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
    filename = "/Users/vijender/Documents/Intern/indpaasx/vision/resources/pdfs/amc/sbi/sbi_6_ADBPB4295N_unlckd_reptd_redacted_merged.pdf"

    tables = read_pdf(filename,
                      flavor='stream', table_areas=["0,4776,595,4577"])

    pprint(tables[0].df)


if __name__ == "__main__":
    main()
