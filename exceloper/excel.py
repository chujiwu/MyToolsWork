from openpyxl import load_workbook
from openpyxl.worksheet import Worksheet


class ExcelSheet(object):
    def __init__(self, sheet: Worksheet):
        self._sheet = sheet

    def get_value_by_column(self, column_name):
        res = []
        tar_column_index = -1
        pre_combine_value = None
        for row in self._sheet:
            for cell in row:
                if cell.value == column_name:
                    tar_column_index = cell.col_idx
                    continue
                if tar_column_index != -1:
                    if cell.col_idx == tar_column_index:
                        if cell.value is not None and cell.coordinate not in self._sheet.merged_cells:
                            res.append(cell.value)
                        if cell.value is None and cell.coordinate not in self._sheet.merged_cells:
                            res.append(cell.value)
                        if cell.value is not None and cell.coordinate in self._sheet.merged_cells:
                            res.append(cell.value)
                            pre_combine_value = cell.value
                        if cell.value is None and cell.coordinate in self._sheet.merged_cells:
                            res.append(pre_combine_value)
        return res


def read_excel(f_p, sheet):
    wb = load_workbook(f_p)
    ws = wb[sheet]
    return ExcelSheet(ws)





if __name__ == "__main__":
    import os
    from xml.etree import ElementTree

    def check_path(fp, ip):
        l = []
        if os.path.exists(fp):
            res = False
            xml = ElementTree.parse(fp)
            for bitmap in xml.iter("Bitmap"):
                l.append(bitmap.attrib["strFileName"])
                if bitmap.attrib["strFileName"] == ip:
                    res = True
                    print("matched")
                    break
            if not res:
                print("Not Matched : " + fp)
                print("form : ")
                print(l)
                print("searched : " + ip)




    folder = "D:\\16.インテック／タダノ／フォーム変換\\11.xml(修正後)"
    es = read_excel(
        "C:\\Users\\xin.cheng\\Desktop\\temp\\for check\\イメージ・リンクフォーム・[サブフォームと繰り返しの併用][複数サブフォームの使用]の抽出結果.xlsx",
        "イメージリスト")
    form_name_list = es.get_value_by_column("フォーム名")
    image_kind_list = es.get_value_by_column("イメージの種類(現行環境)")
    path_new_list = es.get_value_by_column("イメージファイルパス(新環境)")
    fname_new_list = es.get_value_by_column("イメージファイル名(現行環境)")
    path_old_list = es.get_value_by_column("イメージファイルパス(現行環境)")
    fname_old_list = es.get_value_by_column("イメージファイル名（新環境）")

    for i in range(0, len(form_name_list) - 1):
        if image_kind_list[i] == "設計時に設定":
            if path_new_list[i] == "現行と同様":
                check_path(os.path.join(folder, form_name_list[i]).replace(".frm", ".xml"), path_old_list[i] + "\\" + fname_old_list[i])
            elif path_new_list[i] == "回答待ち":
                pass
            elif path_new_list[i] is None:
                pass
            else:
                check_path(os.path.join(folder, form_name_list[i]).replace(".frm", ".xml"), path_new_list[i] + "\\" + fname_new_list[i])
        # print(form_name_list[0])
        # print(image_kind_list[0])
        # print(path_new_list[0])
        # print(path_old_list[0])

