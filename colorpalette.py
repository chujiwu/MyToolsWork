import os
import chardet
from xml.etree import ElementTree

COLOR_WHITE = "0,0,0"
COLOR_BLACK = "255,255,255"


def scan_all_file(folder_path, suffix):
    f_list = os.listdir(folder_path)
    for f in f_list:
        full_path = os.path.join(folder_path, f)
        if os.path.isfile(full_path) and str(f).endswith(suffix):
            yield full_path
        elif os.path.isdir(full_path):
            for f_child in scan_all_file(full_path, suffix):
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
    def __init__(self, xml: ElementTree.ElementTree):
        self._xml = xml
        self._color_palette = {}

    @property
    def color_palette(self):
        return self._color_palette

    def analyze_color(self):
        for color_palette in self._xml.iter("ColorPalette"):
            self._color_palette = color_palette.attrib

    def get_hidden_color_start_idx(self):
        idx = ""
        black_first_shown = False
        for k in self._color_palette:
            if self._color_palette[k] == COLOR_BLACK:
                black_first_shown = True
                idx = k
            if black_first_shown:
                if self._color_palette[k] != COLOR_BLACK:
                    black_first_shown = False
                    idx = False
                else:
                    break

        return idx


class XmlColor(PaletteColor):
    def __init__(self, xml: ElementTree.ElementTree):
        super().__init__(xml)
        self._color_items = []
        self._color_list_not_used = []
        self._item_color_dict = {}

    GRADIENTCOLOR1 = "gradientColor1"
    GRADIENTCOLOR2 = "gradientColor2"
    COLORINDEXES = "colorIndexes"
    PAINTCOLORINDEXES = "paintColorIndexes"

    @property
    def color_list_not_used(self):
        return self._color_list_not_used

    @property
    def item_color_dict(self):
        return self._item_color_dict

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
            if item.attrib[self.GRADIENTCOLOR1] != "":
                color_dict[self.GRADIENTCOLOR1] = item.attrib[self.GRADIENTCOLOR1]
                color_list_in_items.append(item.attrib[self.GRADIENTCOLOR1])
                self._item_color_dict[item.attrib[self.GRADIENTCOLOR1]] = super().color_palette[
                    item.attrib[self.GRADIENTCOLOR1]]
            if item.attrib[self.GRADIENTCOLOR2] != "":
                color_dict[self.GRADIENTCOLOR2] = item.attrib[self.GRADIENTCOLOR2]
                color_list_in_items.append(item.attrib[self.GRADIENTCOLOR2])
                self._item_color_dict[item.attrib[self.GRADIENTCOLOR2]] = super().color_palette[
                    item.attrib[self.GRADIENTCOLOR2]]
            if item.attrib[self.COLORINDEXES] != "":
                color_dict[self.COLORINDEXES] = item.attrib[self.COLORINDEXES]
                color_list_in_items.append(item.attrib[self.COLORINDEXES])
                self._item_color_dict[item.attrib[self.COLORINDEXES]] = super().color_palette[
                    item.attrib[self.COLORINDEXES]]
            if item.attrib[self.PAINTCOLORINDEXES] != "":
                color_dict[self.PAINTCOLORINDEXES] = item.attrib[self.PAINTCOLORINDEXES]
                color_list_in_items.append(item.attrib[self.PAINTCOLORINDEXES])
                self._item_color_dict[item.attrib[self.PAINTCOLORINDEXES]] = super().color_palette[
                    item.attrib[self.PAINTCOLORINDEXES]]
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
    idx_int = int(start_update_idx[1])
    for line in read_lines:
        if "<ColorPalette" in line:
            for color in update_color_list:
                color_for_update_str = "c" + str(idx_int) + "=\"255,255,255\""
                color_updated_str = "c" + str(idx_int) + "=\"" + color + "\""
                line.replace(color_for_update_str, color_updated_str)
                idx_int += 1
    return read_lines

def update_color_palette(cp_path, palette_color: PaletteColor, xml_color_list: [XmlColor]):
    read_lines = _read_file(cp_path)
    update_color_list = get_all_update_color(cp_xml, xml_color_list)
    read_lines = update_cp_content(read_lines, update_color_list, palette_color.get_hidden_color_start_idx())
    # TODO


if __name__ == "__main__":
    cp_path = "C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\color\\color.plt"
    cp_xml = ElementTree.parse(cp_path)
    palette_color = PaletteColor(cp_xml)
    palette_color.analyze_color()
    xml_color_list = []
    for f in scan_all_file("C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\color", ".xml"):
        xml = ElementTree.parse(f)
        xml_color = XmlColor(xml)
        xml_color.analyze_color()
        xml_color_list.append(xml_color)
    update_color_palette(cp_path, palette_color, xml_color_list)
    # f = open("C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\test.xml", "rb")
    # s = f.read()
    # encode_dict = chardet.detect(s)
    # with open("C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\test.xml", "r", encoding=encode_dict["encoding"]) as xml_file:
    #     lines = xml_file.readlines()
    #     for line in lines:
    #         if "<ColorPalette" in line:
    #             print(line)
    # xml_file.close()
