import os
import chardet
from xml.etree import ElementTree

COLOR_WHITE = "0,0,0"
COLOR_BLACK = "255,255,255"


def scan_all_file(folder_path, suffix, excepet_suffix):
    f_list = os.listdir(folder_path)
    for f in f_list:
        full_path = os.path.join(folder_path, f)
        if os.path.isfile(full_path) and str(f).endswith(suffix) and not str(f).endswith(excepet_suffix):
            yield full_path
        elif os.path.isdir(full_path):
            for f_child in scan_all_file(full_path, suffix, excepet_suffix):
                yield f_child
        else:
            pass


def _read_file(f_p):
    file = open(f_p, "rb")
    s_bytes = file.read()
    encode_dict = chardet.detect(s_bytes)
    with open(f_p, "r", encoding=encode_dict["encoding"]) as file_encoded:
        lines = file_encoded.readlines()
    return lines


class PaletteColor(object):
    def __init__(self, xml, f_p: str):
        self._xml = xml
        self._path = f_p
        self._color_palette = {}

    @property
    def color_palette(self):
        return self._color_palette

    @property
    def path(self):
        return self._path

    def analyze_color(self):
        for color_palette in self._xml.iter("ColorPalette"):
            self._color_palette = color_palette.attrib

    def get_hidden_color_start_idx(self):
        idx = ""
        black_first_shown = False
        for k in self._color_palette:
            if not black_first_shown and self._color_palette[k] == COLOR_BLACK:
                black_first_shown = True
                idx = k
                continue
            if black_first_shown:
                if self._color_palette[k] != COLOR_BLACK:
                    black_first_shown = False
                    idx = False
                else:
                    break

        return idx


class XmlColor(PaletteColor):
    def __init__(self, xml: ElementTree.ElementTree, f_p: str):
        super().__init__(xml, f_p)
        self._color_items = []
        self._color_list_not_used = []
        self._item_color_dict = {}

    COLOR_ATTRIB_LIST = [
        "gradientColor1",
        "gradientColor2",
        "colorIndexes",
        "paintColorIndexes"
    ]

    @property
    def color_list_not_used(self):
        return self._color_list_not_used

    @property
    def item_color_dict(self):
        return self._item_color_dict

    @property
    def color_items(self):
        return self._color_items

    @color_items.setter
    def color_items(self, color_items):
        self._color_items = color_items

    def analyze_color(self):
        super().analyze_color()
        self._analyze_color_items()

    def _analyze_color_palette(self):
        for color_palette in self._xml.iter("ColorPalette"):
            super._color_palette = color_palette.attrib

    def _analyze_color_items(self):
        color_list_in_items = []
        for item in self._xml.iter():
            color_dict = {}
            for attrib in self.COLOR_ATTRIB_LIST:
                if attrib in item.attrib:
                    color_index = int(item.attrib[attrib])
                    if color_index != 0:
                        color_index_in_palette = "C" + str(color_index - 1)
                        color_dict[attrib] = [str(color_index), self.color_palette[color_index_in_palette]]
                        color_list_in_items.append(color_index_in_palette)
                        self._item_color_dict[color_index_in_palette] = self.color_palette[color_index_in_palette]
                if color_dict:
                    self._color_items.append((item.tag, item.attrib["name"], color_dict))
        for k in self._color_palette:
            if k not in color_list_in_items:
                self._color_list_not_used.append(k)


def get_all_xml_color_dict(xml_color_list):
    all_xml_color_dict = {}
    for xml_color in xml_color_list:
        xml_color_dict = xml_color.item_color_dict
        all_xml_color_dict.update(xml_color_dict)
    return all_xml_color_dict


def has_no_near_color(color, param):
    # TODO is two color nearly???
    return True


def get_all_update_color(palette_color: PaletteColor, xml_color_list: [XmlColor]):
    update_color = []
    color_palette = palette_color.color_palette
    all_xml_color_dict = get_all_xml_color_dict(xml_color_list)
    for k in all_xml_color_dict:
        color = all_xml_color_dict[k]
        if color not in color_palette.values() and has_no_near_color(color, color_palette.values()):
            update_color.append(color)
    return update_color


def update_cp_content(read_lines, update_color_list, start_update_idx):
    updated_content = []
    idx_int = int(start_update_idx[1:])
    for line in read_lines:
        if "<ColorPalette" in line:
            for color in update_color_list:
                color_for_update_str = "C" + str(idx_int) + "=\"255,255,255\""
                color_updated_str = "C" + str(idx_int) + "=\"" + color + "\""
                line = line.replace(color_for_update_str, color_updated_str)
                idx_int += 1
        updated_content.append(line)
    return updated_content


def update_color_palette(palette_color: PaletteColor, xml_color_list: [XmlColor]):
    read_lines = _read_file(palette_color.path)
    update_color_list = get_all_update_color(palette_color, xml_color_list)
    read_lines = update_cp_content(read_lines, update_color_list, palette_color.get_hidden_color_start_idx())
    print(read_lines)


def update_xml_color_files(palette_color: PaletteColor, xml_color_list: [XmlColor]):
    for xml_color in xml_color_list:
        update_xml_color(palette_color, xml_color)


def replace_xml_color_palette(line, palette_color: PaletteColor):
    updated_line = ""
    palette_color_lines = _read_file(palette_color.path)
    for line in palette_color_lines:
        if "<ColorPalette" in line:
            updated_line = line
    return updated_line


def update_item_color(line, color_item, color_palette):
    attrib_color_dict = {}
    if "name=\"" + color_item[1] in line:
        attrib_color_dict = color_item[2]
        for attrib in attrib_color_dict:
            color = attrib_color_dict[attrib][1]
            for palette_color_index in color_palette:
                if color == color_palette[palette_color_index]:
                    old_str = attrib + "=\"" + attrib_color_dict[attrib][0] + "\""
                    new_str = attrib + "=\"" + str(int(palette_color_index[1:]) + 1) + "\""
                    line = line.replace(old_str, new_str)
    return line


def update_xml_color(palette_color: PaletteColor, xml_color: XmlColor):
    updated_lines = ""
    xml_lines = _read_file(xml_color.path)
    for line in xml_lines:
        if "<ColorPalette" in line:
            line = replace_xml_color_palette(line, palette_color)
        for color_item in xml_color.color_items:
            if "<" + color_item[0] + " " in line:
                line = update_item_color(line, color_item, palette_color.color_palette)
        updated_lines += line
    print(updated_lines)


if __name__ == "__main__":
    cp_path = os.path.join(os.getcwd(), "temp", "color.plt.xml")
    cp_xml = ElementTree.parse(cp_path)
    palette_color = PaletteColor(cp_xml, cp_path)
    palette_color.analyze_color()
    xml_color_list = []
    for f in scan_all_file(os.path.join(os.getcwd(), "temp"), ".xml", ".plt.xml"):
        xml = ElementTree.parse(f)
        xml_color = XmlColor(xml, f)
        xml_color.analyze_color()
        xml_color_list.append(xml_color)
    update_color_palette(palette_color, xml_color_list)
    print("--------------------------------")
    print("--------------------------------")
    update_xml_color_files(palette_color, xml_color_list)
    # f = open("C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\test.xml", "rb")
    # s = f.read()
    # encode_dict = chardet.detect(s)
    # with open("C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\test.xml", "r", encoding=encode_dict["encoding"]) as xml_file:
    #     lines = xml_file.readlines()
    #     for line in lines:
    #         if "<ColorPalette" in line:
    #             print(line)
    # xml_file.close()
