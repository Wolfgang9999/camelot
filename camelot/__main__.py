# -*- coding: utf-8 -*-
import traceback
from tabulate import tabulate
import utils

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

    def preprocess_pdf(
            filename,
            layout_kwargs={}
    ):
        layout, dimensions = utils.get_page_layout(filename, **layout_kwargs)
        images = utils.get_text_objects(layout, ltype="image")
        horizontal_text = utils.get_text_objects(layout, ltype="horizontal_text")
        vertical_text = utils.get_text_objects(layout, ltype="vertical_text")
        preprocess_kwargs = {
            'layout': layout,
            'dimensions': dimensions,
            'images': images,
            'horizontal_text': horizontal_text,
            'vertical_text': vertical_text
        }
        return preprocess_kwargs

    filename = "/Users/atul.rana/Code/indpaasx/vision/resources/pdfs/amc/sbi/sbi_6_ADBPB4295N_unlckd_reptd_redacted_merged.pdf"
    layout_kwargs = {}


    preprocess_kwargs = preprocess_pdf(filename, layout_kwargs)
    tables = read_pdf(
        filepath=filename,
        preprocess_kwargs=preprocess_kwargs,
        flavor='stream',
        table_areas=["0,4776,595,4577"]
    )
    data = tables[0].df
    pprint(data)


if __name__ == "__main__":
    main()
