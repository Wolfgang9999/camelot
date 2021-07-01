# -*- coding: utf-8 -*-

import os

from ..utils import get_page_layout, get_text_objects


class BaseParser(object):
    """Defines a base parser.
    """

    def _generate_layout(
        self, filename, page, layout_kwargs,
        layouts, dimensions, **kwargs
    ):
        self.filename = filename
        self.layout_kwargs = layout_kwargs
        self.horizontal_text, self.dimensions = layouts[page-1], dimensions
        self.pdf_width, self.pdf_height = self.dimensions
        self.rootname, __ = os.path.splitext(self.filename)
