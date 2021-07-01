import ast
import re
import time
import pdfquery
from lxml import etree
from pdfminer.pdftypes import resolve1
from pdfquery.pdfquery import _flatten, parser, obj_to_string, LayoutElement, strip_invalid_xml_chars
from pdfminer.layout import LTChar, LTImage, LTPage, LTLine, LTRect, LTCurve, LTTextLineHorizontal



def get_bbox_layout(candidate):
    bbox = candidate.get('bbox')
    bbox = ast.literal_eval(bbox)
    return tuple(bbox)


def _xmlize(self, node, root=None):
    if isinstance(node, LayoutElement):
        # Already an XML element we can use
        # print(node._layout)
        branch = node
    else:
        # collect attributes of current node
        tags = self._getattrs(
            node, 'y0', 'y1', 'x0', 'x1', 'width', 'height', 'bbox',
            'linewidth', 'pts', 'index', 'name', 'matrix', 'word_margin'
        )
        if type(node) == LTImage:
            tags.update(self._getattrs(
                node, 'colorspace', 'bits', 'imagemask', 'srcsize',
                'stream', 'name', 'pts', 'linewidth')
            )
        elif type(node) == LTChar:
            tags.update(self._getattrs(
                node, 'fontname', 'adv', 'upright', 'size')
            )
        elif type(node) == LTPage:
            tags.update(self._getattrs(node, 'pageid', 'rotate'))

        # create node
        branch = parser.makeelement(node.__class__.__name__, tags)

    branch.layout = node
    self._elements += [branch]  # make sure layout keeps state
    if root is None:
        root = branch

    # add text
    if hasattr(node, 'get_text'):
        branch.text = strip_invalid_xml_chars(node.get_text())

    # add children if node is an iterable
    if hasattr(node, '__iter__') and not isinstance(node, LTTextLineHorizontal):
        last = None
        for child in node:
            if not (isinstance(child, LTCurve) or isinstance(child, LTRect) or isinstance(child, LTLine) or isinstance(child, LTImage)):
                child = _xmlize(self, child, root)
                branch.append(child)
                last = child

    return branch


def get_tree(self, *page_numbers, layouts=None):
    """
        Return lxml.etree.ElementTree for entire document, or page numbers
        given if any.
    """
    cache_key = "_".join(map(str, _flatten(page_numbers)))
    tree = self._parse_tree_cacher.get(cache_key)
    layout = []
    if tree is None:
        # set up root
        root = parser.makeelement("pdfxml")
        if self.doc.info:
            for k, v in list(self.doc.info[0].items()):
                k = obj_to_string(k)
                v = obj_to_string(resolve1(v))
                try:
                    root.set(k, v)
                except ValueError as e:
                    # Sometimes keys have a character in them, like ':',
                    # that isn't allowed in XML attribute names.
                    # If that happens we just replace non-word characters
                    # with '_'.
                    if "Invalid attribute name" in e.args[0]:
                        k = re.sub('\W', '_', k)
                        root.set(k, v)

        if layouts is not None:
            n = 0
            for layout in layouts:
                layout = _xmlize(self, layout)
                layout.set('page_index', obj_to_string(n))
                layout.set('page_label', self.doc.get_page_number(n))
                root.append(layout)
                n += 1
            self._clean_text(root)

        # Parse pages and append to root.
        # If nothing was passed in for page_numbers, we do this for all
        # pages, but if None was explicitly passed in, we skip it.
        elif not (len(page_numbers) == 1 and page_numbers[0] is None):
            if page_numbers:
                pages = [[n, self.get_layout(self.get_page(n))] for n in
                         _flatten(page_numbers)]
            else:
                pages = enumerate(self.get_layouts())
            for n, page in pages:
                layout.append(page)
                page = _xmlize(self, page)
                page.set('page_index', obj_to_string(n))
                page.set('page_label', self.doc.get_page_number(n))
                root.append(page)
            self._clean_text(root)

        # wrap root in ElementTree
        tree = etree.ElementTree(root)
        self._parse_tree_cacher.set(cache_key, tree)
    return tree, layout[0]


def load(obj, *page_numbers):
    obj.tree, layout = get_tree(obj, *_flatten(page_numbers))
    obj.pq = obj.get_pyquery(obj.tree)
    return obj.tree, layout, obj.pq


def load_pdf_and_layout(file_path, num_pages):
    pdfquery_params = {'char_margin': 1, 'line_margin': 0.5, 'word_margin': 0.1, 'detect_vertical': True,
                       'all_texts': True, }
    laparams = {**pdfquery_params}
    pdf = pdfquery.PDFQuery(file=file_path, resort=False,
                            laparams=laparams)
    pq_obj = {}
    layouts = []
    st1 = time.time()
    for page_no in range(0, num_pages):
        pq_obj[page_no] = None
        tree, layout, pq_obj[page_no] = load(pdf, page_no)
        layouts.append(layout)
    return layouts


def preprocess_pdf(layouts, num_pages):
    # layout, dimensions = camelot.utils.get_page_layout(filename, **layout_kwargs)
    if len(layouts) != num_pages:
        raise Exception('Unable to find layout for all the pages.')
    width = layouts[0].bbox[2]
    height = layouts[0].bbox[3]
    dimensions = (width, height)
    preprocess_kwargs = {
        'layout': layouts,
        'dimensions': dimensions
    }
    return preprocess_kwargs


if __name__ == '__main__':
    file_path = "/Users/vijender/Documents/Intern/improved_indpaasx/indpaasx/vision/resources/pdfs/ecas/ABKPP9241K_unlckd_reptd_redacted_merged_page-1.pdf"
    # merged_file_path = "/Users/vijender/Downloads/NSDLe-CAS_100851700_FEB_2021_unlckd_unlckd_reptd_redacted_merged_page-1.pdf"
    pdf, layouts = load_pdf_and_layout(file_path, {})
    pdf.tree.write('sample_1.xml', pretty_print=True)
    st = time.time()
    layout_kwargs = {}
    # page = camelot.utils.get_page_layout(file_path, **layout_kwargs)
    print("final_time", time.time() - st)
    # pdf, layouts = load_pdf_and_layout(file_path, {})

    # pdf.tree.write('sample.xml', pretty_print=True)
