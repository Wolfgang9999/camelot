import os

from ..utils import get_page_layout
from ..utils import get_text_objects


class BaseParser:
    """Defines a base parser."""

    def _generate_layout(
        self, filename, layout_kwargs,
        layout, dimensions, images,
        horizontal_text, vertical_text,
        **kwargs
    ):
        self.filename = filename
        self.layout_kwargs = layout_kwargs
        self.layout, self.dimensions = layout, dimensions  # get_page_layout(filename, **layout_kwargs)
        self.images = images
        self.horizontal_text = horizontal_text
        self.vertical_text = vertical_text
        self.pdf_width, self.pdf_height = self.dimensions
        self.rootname, __ = os.path.splitext(self.filename)
        self.imagename = "".join([self.rootname, ".png"])
