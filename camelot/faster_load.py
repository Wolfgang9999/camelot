import copy

import fitz
import time
from lxml import etree as ET
from pdfquery.pdftranslator import PDFQueryTranslator
from pyquery import PyQuery


class BBox:

    def __init__(self, left, bottom, right, top):
        self.bottom = bottom
        self.left = left
        self.top = top
        self.right = right

    def __str__(self):
        return f'bbox={{left: {self.left}, bottom: {self.bottom},  right: {self.right}, top: {self.top}}}'

    def get_coords(self):
        return self.left, self.bottom, self.right, self.top

    def get_top_left_bbox(self, height):
        return self.left, height - self.top, self.right, height - self.bottom


class WordBox:
    def __init__(self, left, bottom, right, top, text):
        self.bottom = bottom
        self.left = left
        self.top = top
        self.right = right
        self.height = abs(top - bottom)
        self.width = abs(right - left)
        self.text = text

    def __str__(self):
        return f'bbox={{left: {self.left}, bottom: {self.bottom},  right: {self.right}, top: {self.top}}}'

    def get_coords(self):
        return self.left, self.bottom, self.right, self.top

    def get_top_left_bbox(self, height):
        return self.left, height - self.top, self.right, height - self.bottom

    def isright(self, obj):
        return self.left < obj.left

    def bbox(self):
        return BBox(self.left, self.bottom, self.right, self.top)

    def add(self, obj):
        if self.isright(obj):
            self.text = self.text + ' ' + obj.text
            self.right = obj.right
        else:
            obj.text = obj.text + ' ' + self.text
            self.left = obj.left
        self.top = max(self.top, obj.top)  # top is below than bottom in coordinate system
        self.bottom = min(self.bottom, obj.bottom)


def is_voverlap(obj1, obj2):
    return obj2.bottom <= obj1.top and obj1.bottom <= obj2.top


def voverlap(obj1, obj2):
    if is_voverlap(obj1, obj2):
        return min(abs(obj1.bottom - obj2.top), abs(obj1.top - obj2.bottom))
    else:
        return 0


def is_hoverlap(obj1, obj2):
    return obj2.left <= obj1.right and obj1.left <= obj2.right


def hdistance(obj1, obj2):
    if is_hoverlap(obj1, obj2):
        return 0
    else:
        return min(abs(obj1.left - obj2.right), abs(obj1.right - obj2.left))


def group_objects(objs, laparams_line_overlap=0.5, laparams_word_margin=0.2):
    line = None
    res = []
    for obj1 in objs:
        if line is None:
            line = obj1
        else:
            halign = is_voverlap(line, obj1) \
                     and min(line.height, obj1.height) * laparams_line_overlap < voverlap(line, obj1) \
                     and hdistance(line, obj1) < laparams_word_margin
            if halign:
                line.add(obj1)
            else:
                if line.height < 80:
                    res.append(line)
                line = obj1
    if line is not None and line.height < 80:
        res.append(line)
    return res


def get_lt_page_line(page_index, y0, y1, bbox):
    return f'<LTPage id="{page_index}" y0="{y0}" y1="{y1}" bbox="{bbox}">'


def get_lt_word_line(word):
    word_bbox = list(word.get_coords())
    text = word.text.replace("<", " ")
    text = text.replace(">", " ")
    text = text.replace("/", " ")
    text = text.replace("&", " ")
    str = f'<LTWord x0="{word.left}" y0="{word.bottom}" x1="{word.right}" y1="{word.top}" bbox="{word_bbox}">{text}</LTWord>'
    return str


def create_page_tree(page, layouts, page_index, pq_obj):
    page_tree_arr = []
    page_mediabox = page.MediaBox
    bbox = [page_mediabox.x0, page_mediabox.y0, page_mediabox.x1, page_mediabox.y1]
    page_tree_arr.append(get_lt_page_line(page_index, page_mediabox.y0, page_mediabox.y1, bbox))
    word: WordBox
    word_str = "".join([get_lt_word_line(word) for word in layouts[page_index]])
    page_tree_arr.append(word_str)
    page_tree_arr.append('</LTPage>')
    page_tree_str = ''.join(page_tree_arr)
    page_el = ET.fromstring(page_tree_str)

    pq = PyQuery(page_el, css_translator=PDFQueryTranslator())
    pq_obj[page_index] = pq


def get_precomputed_text_boxes(pq_obj, precompute_texts, num_pages):
    precomputed_text_boxes = {}
    total_time = 0
    for label in precompute_texts:
        candidates = {}
        for page_no in range(num_pages):
            st8 = time.time()
            boxes = pq_obj[page_no](f'LTWord:contains("{label}")')
            total_time += (time.time() - st8)
            candidates[page_no] = boxes
        precomputed_text_boxes[label] = candidates
    print(total_time)
    return precomputed_text_boxes


def load_pdf_and_layout(file_path, conf):
    pdfquery_params = {'word_margin': 5, 'line_overlap': 0.5}
    conf_pdfquery_params = conf.get('pdfquery_params', {})
    laparams = {**pdfquery_params, **conf_pdfquery_params}
    doc = fitz.open(file_path)
    page_index = 0
    layouts = {}
    pq_obj = {}
    height = doc[0].MediaBox.height
    width = doc[0].MediaBox.width
    for page in doc:
        words = page.get_text("words")
        words_objs = []
        for word in words:
            word_box = WordBox(word[0], height - word[3], word[2], height - word[1], word[4])
            words_objs.append(word_box)
        layouts[page_index] = group_objects(words_objs, laparams_line_overlap=laparams["line_overlap"],
                                            laparams_word_margin=laparams["word_margin"])
        create_page_tree(page, layouts, page_index, pq_obj)
        page_index += 1
    dimensions = (width, height)
    return layouts, pq_obj, dimensions


if __name__ == '__main__':
    st = time.time()
    # fname = '/Users/vijender/Downloads/trade_details_ABPXXXXX2J_1567897540_unlckd.pdf'
    # fname = '/Users/vijender/Documents/Intern/improved_indpaasx/indpaasx/vision/resources/pdfs/ecas/Apspd6433R@_9190_unlckd.pdf'
    fname = '/Users/vijender/Documents/Intern/improved_indpaasx/indpaasx/vision/resources/pdfs/ecas/ABKPP9241K_unlckd.pdf'

    layout, pq_obj, dimensions = load_pdf_and_layout(fname, {})
    boxes = pq_obj[2](f'LTWord:contains("Folio No")')
    for box in boxes:
        print(box.get("bbox"))





    # for page in doc:
    #     words = page.get_text("words")
    #     words_objs = []
    #     for word in words:
    #         word_box = WordBox(word[0], height - word[3], word[2], height - word[1], word[4])
    #         words_objs.append(word_box)
    #     layout[page_index] = group_objects(words_objs)
    #     create_page_tree(page, layout, page_index, pq_obj)
    #     # print("create_page_tree", time.time() - st4)
    #     page_index += 1

    # tree = combine_all_tree(trees)
    # print(time.time() - st5)
    # st6 = time.time()
    # final_tree = xml_rewrite(tree, page_index, height)
    # final_pq = PyQuery(final_tree, css_translator=PDFQueryTranslator())
    # st8 = time.time()
    # print(final_pq(f'LTWord:contains("Amount")'))
    # print(time.time() - st8)
    print(time.time() - st)
    # bboxes = []
    # for word in group_objects(words_objs):
    #     bboxes.append(word.get_coords())

    # draw_on_pdf(fname, bboxes)
