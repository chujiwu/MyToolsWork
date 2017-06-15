import os
import chardet

UTF8_BOM = bytearray(b'\xEF\xBB\xBF')


def check_bom(p):
    f = open(p, "rb")
    s = f.read()
    print(f.name[len("D:\\16.インテック／タダノ／フォーム変換\\20.テストデータ") + 1:], chardet.detect(s))
    if s.startswith(UTF8_BOM):
        print(f.name, "BOM")


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

if __name__ == "__main__":
    for f_p in scan_all_file("D:\\16.インテック／タダノ／フォーム変換\\11.xml(修正後)", ".xml"):
        check_bom(f_p)
