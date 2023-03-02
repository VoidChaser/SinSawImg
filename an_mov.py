import asyncio
import sys
import os
from time import ctime, time
from vibor_new import Ui_MainWindow
import datetime as dt
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPixmap
from PIL import Image


# import scipy


from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractButton
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem

PHOTOFORMATS = ['img', 'bmp', 'raw', 'png', 'jpg', 'jpeg', 'IMG', 'BMP', 'RAW', 'PNG', 'JPG', 'JPEG']
print(PHOTOFORMATS)

days = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}
# async def saved(item, outpath):
#     item.save(outpath)
#     return ''


async def componented_less_variety(in_path, out_path):
    im = Image.open(in_path)
    x, y = im.size

    im2 = im.resize((x // 3, y // 3))
    print(f"{out_path} saved")
    im2.save(out_path)
    await asyncio.sleep(1/10000)

# async def componented_less_variety(in_path, out_path):
#     im = Image.open(in_path)
#     x, y = im.size
#     im2 = im.resize((x // 3, y // 3))
#     print(f"{out_path} saved")
#     await im2.save(out_path)

# async def componented_less_variety(in_path, out_path):
#     im = Image.open(in_path)
#     x, y = im.size
#     im2 = im.resize((x // 3, y // 3))
#     print(f"{out_path} saved")
#     asyncio.create_task(im2.save(out_path))



# def less_variety(in_path, out_path):
#     im = Image.open(in_path)
#     x, y = im.size
#
#     im2 = im.resize((x // 3, y // 3))
#     im2.save(out_path)
#     return f"{out_path} saved"


def get_formated(data):
    not_date = list(filter(lambda x: x != '', ctime(data).split(' ')))
    f = f"{not_date[2].rjust(2, '0')}.{days[not_date[1]]}.{not_date[-1]} {not_date[-2]}"
    ff = dt.datetime.strptime(f, "%d.%m.%Y %H:%M:%S")
    fff = ff.strftime("%d.%m.%Y %H:%M:%S")
    return fff


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.tableWidget.cellClicked.connect(self.show_selected_items)

        self.tableWidget.itemSelectionChanged.connect(self.show_selected_items)
        self.tableWidget.pressed.connect(self.show_selected_items)

        self.current_selection = []
        self.min_path = ''
        self.current_image_path = ''
        self.imported_dirs = []
        self.preview_position = 0
        self.formated_infos = []

        self.cornerbutton = QObject.findChild(self.tableWidget, QAbstractButton)
        self.cornerbutton.clicked.connect(self.show_selected_items)
        self.go_left_button.clicked.connect(self.change_img_preview)
        self.go_right_button.clicked.connect(self.change_img_preview)
        self.go_start_button.clicked.connect(self.change_img_preview)
        self.go_end_button.clicked.connect(self.change_img_preview)
        self.run()
        self.showNormal()


    def show_selected_items(self):
        # print('Unformated in =')
        unformatted_selection = list(map(lambda x: x.text(), self.tableWidget.selectedItems()))
        # print(unformatted_selection)
        formated_selection = []
        # print('contains: \n')
        for _ in range(0, len(unformatted_selection), 5):
            # print(unformatted_selection[_:_ + 5])
            formated_selection.append(unformatted_selection[_:_ + 5])
        self.current_selection = formated_selection
        # print(self.current_selection)
        self.preview_position = 0
        self.show_imgs_preview()

    def show_imgs_preview(self):
        self.preview_size = self.image.size()
        self.preview_sizes = (self.preview_size.width(), self.preview_size.height())
        # print(self.preview_sizes)

        if self.current_selection:
            self.preview_position = self.preview_position % len(self.current_selection)
            self.current_image_path = self.min_path + '/' + self.current_selection[self.preview_position][0]
            self.true_path = self.current_selection[self.preview_position][-1]
            self.name_out_label.setText(f"{self.preview_position + 1}/{len(self.current_selection)}, {self.true_path}")
            self.pixmap = QPixmap(self.current_image_path)
            self.pixmap = self.pixmap.scaled(*self.preview_sizes, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.image.setPixmap(self.pixmap)

    def change_img_preview(self):
        if self.sender().text() == '<-':
            self.preview_position = self.preview_position - 1
        elif self.sender().text() == '->':
            self.preview_position = self.preview_position + 1
        elif self.sender().text() == '<<-':
            self.preview_position = 0
        elif self.sender().text() == '->>':
            self.preview_position = len(self.current_selection) - 1
        self.show_imgs_preview()

    async def create_miniatures_folder_with(self):
        tasks = []

        self.min_path = self.dir_name + '/miniatures'
        if not os.path.exists(self.min_path):
            os.makedirs(self.min_path)

        for __ in self.formated_infos:
            curr_name = __[0]
            taks = componented_less_variety(__[-1], self.min_path + '/' + curr_name)
            tasks.append(taks)

        await asyncio.gather(*tasks)

    def keyPressEvent(self, event):
        # print(event.key())
        kb_key = event.key()
        corners = [91, 93]
        arrows = [16777234, 16777236]
        if kb_key in arrows or kb_key in corners:
            if kb_key == arrows[0]:
                self.preview_position = self.preview_position - 1
            elif kb_key == arrows[1]:
                self.preview_position = self.preview_position + 1
            elif kb_key == corners[0]:
                self.preview_position = 0
            elif kb_key == corners[1]:
                self.preview_position = len(self.current_selection) - 1
            self.show_imgs_preview()

    def resizeEvent(self, event):
        self.show_imgs_preview()

    def add_folder(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)

        self.dir_name = dialog.getExistingDirectory(self, 'Выбрать путь к папке')
        # print(self.dir_name)
        files = list(filter(lambda x: x[0] != '.' and '.' in x, os.listdir(path=self.dir_name)))
        # print(files)
        for __ in range(1, len(files) + 1):
            _ = files[__ - 1]
            typ = _.split('.')[-1]
            file_path = self.dir_name + '/' + _
            if typ in PHOTOFORMATS:
                file_stat = os.stat(file_path)
                self.formated_infos.append(
                    (_, '.' + typ, get_formated(file_stat.st_mtime), get_formated(file_stat.st_ctime), file_path))
        print(self.formated_infos)

    def run(self):
        self.add_folder()
        for i in range(len(self.formated_infos)):
            self.tableWidget.insertRow(i)
            for j, val in enumerate(self.formated_infos[i]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
                # self.tableWidget.adjustSize()
        start_time = time()
        asyncio.run(self.create_miniatures_folder_with())
        print("--- %s seconds ---" % (time() - start_time))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())


# TO DO: написать комментарии. Придумать второе окно, и главное окно. Придумать штуку с тегами. Асинхронность доделать
