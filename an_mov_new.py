import sys
import os
from time import ctime, time, sleep
from vibor_new_dialog_based_other import Ui_MainWindow
import datetime as dt
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPixmap
from PIL import Image
import sqlite3
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractButton
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox

PHOTOFORMATS = ['img', 'bmp', 'raw', 'png', 'jpg', 'jpeg', 'IMG', 'BMP', 'RAW', 'PNG', 'JPG', 'JPEG']


class DupeError(BaseException):
    pass


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


def get_formated_date(data):
    not_date = list(filter(lambda x: x != '', ctime(data).split(' ')))
    f = f"{not_date[2].rjust(2, '0')}.{days[not_date[1]]}.{not_date[-1]} {not_date[-2]}"
    ff = dt.datetime.strptime(f, "%d.%m.%Y %H:%M:%S")
    fff = ff.strftime("%d.%m.%Y %H:%M:%S")
    return fff


class Example(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initialize_base()
        self.tableWidget.itemSelectionChanged.connect(self.show_selected_items)
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
        self.add_tag_button.clicked.connect(self.add_tag)
        self.delete_tag_button.clicked.connect(self.delete_tag)
        self.add_folder_button.clicked.connect(self.add_folder)
        self.dupe_check_button.clicked.connect(self.dupe_check)
        self.deselect_button.clicked.connect(self.deselect)
        self.delete_selected_img_button.clicked.connect(self.delete_image)
        self.go_end_button.clicked.connect(self.change_img_preview)
        self.add_images_from_folder_button.clicked.connect(self.add_image)
        self.run()
        self.showNormal()

    def create_miniature(self, in_path):
        im = Image.open(in_path)
        x, y = im.size
        file_name = in_path.split('/')[-1]
        out_path = self.min_path + '/' + file_name
        # print(out_path)

        im2 = im.resize((x // 3, y // 3))
        print(f"{out_path} saved")
        im2.save(out_path)
        return self.run_dir + '/' + out_path

    def show_selected_items(self):
        unformated_selection = list(map(lambda x: x.text(), self.tableWidget.selectedItems()))
        print(unformated_selection)
        formated_selection = []
        for _ in range(0, len(unformated_selection), 6):
            formated_selection.append(unformated_selection[_:_ + 6])
        self.current_selection = formated_selection
        self.preview_position = 0
        self.navigation_tagging_checking_buttons_state_initialize()
        self.show_imgs_preview()

    def show_imgs_preview(self):
        self.preview_size = self.image_label.size()
        self.preview_sizes = (self.preview_size.width(), self.preview_size.height())
        if self.current_selection:
            self.preview_position = self.preview_position % len(self.current_selection)
            self.name_out_label.setText(
                f"{self.preview_position + 1}/{len(self.current_selection)},"
                f" {self.current_selection[self.preview_position][1]}")
            self.pixmap = QPixmap(self.current_selection[self.preview_position][-1])
            self.pixmap = self.pixmap.scaled(*self.preview_sizes, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.image_label.setPixmap(self.pixmap)

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

    def dupe_check(self):
        self.initialize_base()
        tags_dupped = []
        already_tag_names = []
        for _ in self.tags:
            if _[1] not in already_tag_names:
                already_tag_names.append(_[1])
            else:
                tags_dupped.append(_)


        imgs_duped = []
        already_imgs = []
        for _ in self.images:
            if _[1:-1] not in already_imgs:
                already_imgs.append(_[1:-1])
            else:
                imgs_duped.append(_)

        if not tags_dupped and not imgs_duped:
            self.log_out_label.setText('Всё в порядке. Дубли отстутвуют.')
            return

        if tags_dupped:
            valid = QMessageBox.question(
                self, '', "Среди тэгов обнаружены дубли. Убрать дубли из тэгов?",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                for _ in tags_dupped:
                    self.curs.execute(
                        f'''delete from tags where id = '{_[0]}' 
''').fetchall()
                    self.base_conection.commit()
                    self.initialize_base()
                    self.log_out_label.setText('Дубли были удалены из тэгов.')
        elif not tags_dupped:
            self.log_out_label.setText('Дублей нет в тэгах.')

        if imgs_duped:
            valid = QMessageBox.question(
                self, '', "Среди изображений обнаружены дубли. Убрать дубли из изображений?",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                for _ in imgs_duped:
                    self.log_out_label.setText(f"Изображение {_[1]} удалено")
                    self.curs.execute(
                        f'''delete from images where id = '{_[0]}' 
            ''').fetchall()
                    self.base_conection.commit()
                    self.initialize_base()
                    self.log_out_label.setText('Дубли были удалены из изображений')
        elif not imgs_duped:
            self.log_out_label.setText('Дублей нет в изображениях.')
        self.deselect()
        self.initialize_base()
        self.table_widget_initialize()

    def keyPressEvent(self, event):
        if all(list(map(lambda x: x.isEnabled(), self.navigation_arrows_button_group.buttons()))):
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

    def add_images_to_base(self, li):
        for ___ in li:
            path, tip, c_date, m_date, mini_path = ___

            self.log_out_label.setText(f"Папка {''.join(path.split('/')[:-1])} добавлена")
            self.curs.execute(f'''INSERT INTO images (path, type, modified_date, creation_date, mini_path)
            VALUES ('{path}', '{tip}', '{c_date}', '{m_date}', '{mini_path}')''').fetchall()
            self.base_conection.commit()
        self.initialize_base()

    def go_add_or_not_dialogue_folder_add(self):
        valid = QMessageBox.question(
            self, '', "Возникла ошибка при добавлении папки. Попробовать еще раз?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.add_folder()

    def go_add_or_not_dialogue_image_add(self):
        valid = QMessageBox.question(
            self, '', "Возникла ошибка при добавлении изображения(ий). Попробовать еще раз?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.add_image()

    def go_add_or_not_dialogue_tag_add(self):
        valid = QMessageBox.question(
            self, '', "Возникла ошибка при добавлении тэга. Попробуйте еще раз.",
            QMessageBox.Ok)
        if valid == QMessageBox.Ok:
            pass

    def add_folder(self):
        self.deselect()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        try:
            self.dir_name = dialog.getExistingDirectory(self, 'Выбрать путь к папке с изображениями')
            photo_files = list(filter(lambda z: z[1] in PHOTOFORMATS, list(
                map(lambda y: [self.dir_name + '/' + y, y.split('.')[-1]],
                    (filter(lambda x: x[0] != '.' and '.' in x, os.listdir(path=self.dir_name)))))))
            print(photo_files)

            if not photo_files:
                raise ImportError('В папке нет изображений. Выберите папку с изображениями.')
            if self.images:
                imgs_duped = list(filter(lambda x: x in list(map(lambda z: z[1], self.images)),
                                         list(map(lambda x: x[0], photo_files))))
                print(imgs_duped)
                if imgs_duped == photo_files:
                    raise DupeError('Все изображения в папке уже добавлены.')
                else:
                    photo_files = list(filter(lambda x: x not in imgs_duped, photo_files))

            for _ in photo_files:
                o_p = self.create_miniature(_[0])
                file_stat = os.stat(_[0])
                _.extend([get_formated_date(file_stat.st_mtime), get_formated_date(file_stat.st_ctime), o_p])

            self.formated_infos = photo_files
            self.add_images_to_base(self.formated_infos)
            self.table_widget_initialize()

        except FileNotFoundError:
            self.log_out_label.setText('Некорректно указана директория папки с изображениями')
            self.go_add_or_not_dialogue_folder_add()

        except ImportError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_folder_add()

        except DupeError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_folder_add()

    def add_image(self):
        self.deselect()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        try:
            image_path = dialog.getOpenFileNames(self, 'Выбрать путь к изображению(ям)')[0]
            photo_files = list(map(lambda u: u[0], list(filter(lambda z: z[1] in PHOTOFORMATS, list(
                map(lambda y: [y, y.split('.')[-1]],
                    (filter(lambda x: x[0] != '.' and '.' in x, image_path))))))))
            print(photo_files)

            if not photo_files:
                raise ImportError('Выбранный файл не является изображением(ями).')
            if self.images:
                imgs_duped = list(filter(lambda x: x in list(map(lambda z: z[1], self.images)),
                                         list(map(lambda x: x, photo_files))))
                print(imgs_duped)

                if imgs_duped == photo_files:
                    raise DupeError('Выбранный файл уже добавлен(ы).')
                else:
                    photo_files = list(filter(lambda x: x not in imgs_duped, photo_files[0]))

            for _ in photo_files:
                o_p = self.create_miniature(_[0])
                file_stat = os.stat(_[0])
                _.extend([get_formated_date(file_stat.st_mtime), get_formated_date(file_stat.st_ctime), o_p])

            self.formated_infos = photo_files
            self.add_images_to_base(self.formated_infos)
            self.table_widget_initialize()

        except FileNotFoundError:
            self.log_out_label.setText('Некорректно указан путь к изображению(ям)')
            self.go_add_or_not_dialogue_image_add()

        except ImportError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_image_add()

        except DupeError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_image_add()


    def initialize_base(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)

        self.base_path = os.getcwd() + '/tags_sinsaw.sqlite'
        if not os.path.exists(self.base_path):
            try:
                self.base_path = dialog.getOpenFileName(self, 'Выберите путь к базе')[0]
                if self.base_path == '':
                    raise ValueError('Путь к базе не найден')
                elif self.base_path.split('.')[-1] != 'sqlite':
                    raise AttributeError('Формат базы данных некорректен')
                print(f'Путь к базе данных {self.base_path}')
            except ValueError as exeption:
                print(exeption)
                sys.exit()

            except AttributeError as exeption:
                print(exeption)
                self.initialize_base()
        self.base_conection = sqlite3.connect(self.base_path)
        self.curs = self.base_conection.cursor()

        self.tags = list(self.curs.execute('''select * from tags'''))
        self.images = list(self.curs.execute('''select * from images'''))
        self.image_tags = list(self.curs.execute('''select * from image_tags'''))

        self.check_box_initialize()

    def add_tag(self):
        try:
            tag_name = self.tag_name_edit.text()
            if tag_name == '':
                raise ValueError('Имя тэга не указано.')
            tag_names = list(map(lambda x: x[1], self.tags))
            if tag_name not in tag_names:
                self.tag_name_edit.setText('')
                self.log_out_label.setText(f"Тэг {tag_name} добавлен")
                self.curs.execute(f'''INSERT INTO tags (name)
        VALUES ('{tag_name}');''').fetchall()
                self.base_conection.commit()
                self.initialize_base()
            else:
                raise DupeError('Тэг с таким именем уже существует. Он не был добавлен.')
        except DupeError as exeption:
            self.log_out_label.setText(str(exeption))
            self.tag_name_edit.setText('')
            self.go_add_or_not_dialogue_tag_add()
        except ValueError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_tag_add()

    def delete_tag(self):
        tag_name = self.tag_choose_box.currentText()
        valid = QMessageBox.question(
            self, '', f"Действительно удалить тэг {tag_name}?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.log_out_label.setText(f"Тэг {tag_name} удалён")
            self.curs.execute(
                f'''delete from tags where id = (SELECT id from tags where name = '{tag_name}')''').fetchall()
            self.base_conection.commit()
            self.initialize_base()

    def delete_image(self):
        unformated_selection = list(map(lambda x: x.text(), self.tableWidget.selectedItems()))
        print(unformated_selection)
        formated_selection = []
        for _ in range(0, len(unformated_selection), 6):
            formated_selection.append(unformated_selection[_:_ + 6])
        print(formated_selection)
        valid = QMessageBox.question(
            self, '', f"Действительно удалить эти изображения(е)?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            for _ in formated_selection:
                print(_)
                os.remove(_[-1])
                self.curs.execute(f'''delete from images where id = '{_[0]}'
                ''').fetchall()
                self.base_conection.commit()
            self.tableWidget.clear()
            self.current_selection = []
            self.tableWidget.setColumnCount(0)
            self.tableWidget.setRowCount(0)
            self.initialize_base()
            self.deselect()
            if not self.images:
                self.log_out_label.setText('Изображения были удалены.')
                self.repair_autoincrement()
                sleep(1.0)
                self.dupe_check_button.setEnabled(False)
                self.log_out_label.setText('База изображений пуста. Добавьте изображения(е).')
            else:
                self.log_out_label.setText('Изображения были удалены.')

    def deselect(self):
        self.tableWidget.clearSelection()
        self.name_out_label.setText('')
        self.preview_position = 0
        self.image_label.clear()
        self.navigation_tagging_checking_buttons_state_initialize()

    def navigation_tagging_checking_buttons_state_initialize(self):
        if self.tableWidget.selectedItems():
            for _ in self.navigation_arrows_button_group.buttons():
                _.setEnabled(True)
            for _ in self.tag_redact_button_group.buttons():
                _.setEnabled(True)
            for _ in self.selected_manipulations_button_group.buttons():
                _.setEnabled(True)

        else:
            for _ in self.navigation_arrows_button_group.buttons():
                _.setEnabled(False)
            for _ in self.tag_redact_button_group.buttons():
                _.setEnabled(False)
            for _ in self.selected_manipulations_button_group.buttons():
                _.setEnabled(False)

    def check_box_initialize(self):
        self.tag_choose_box.clear()
        if self.tags:
            self.tag_choose_box.setEnabled(True)
            self.delete_tag_button.setEnabled(True)
            for _ in self.tags:
                self.tag_choose_box.addItem(_[1])
        else:
            self.tag_choose_box.setEnabled(False)
            self.delete_tag_button.setEnabled(False)

    def table_widget_initialize(self):
        res = self.curs.execute("SELECT * from images").fetchall()
        if not res:
            self.name_out_label.setText('Изображения не найдены')
            self.dupe_check_button.setEnabled(False)
            self.add_folder()
        else:
            self.name_out_label.setText('')
            self.tableWidget.setRowCount(len(res))
            self.tableWidget.setColumnCount(len(res[0]))
            self.titles = [title[0] for title in self.curs.description]
            for i, elem in enumerate(res):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.tableWidget.setHorizontalHeaderLabels(self.titles)
            self.dupe_check_button.setEnabled(True)

    def repair_autoincrement(self):
        if not self.tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'tags'
            ''').fetchall()
            self.base_conection.commit()

        elif not self.tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM tags) - 1 WHERE name = 'tags'
            ''').fetchall()
            self.base_conection.commit()

        if not self.images:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'images'
            ''').fetchall()
            self.base_conection.commit()

        elif not self.tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM images) - 1 WHERE name = 'images'
            ''').fetchall()
            self.base_conection.commit()

        if not self.image_tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'image_tags'
            ''').fetchall()
            self.base_conection.commit()

        elif not self.tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM image_tags) - 1 WHERE name = 'image_tags'
            ''').fetchall()
            self.base_conection.commit()

    def run(self):
        self.repair_autoincrement()
        # self.initialize_base()
        print(self.images)
        self.run_time = get_formated_date(time()).split(' ')[::]
        # print(self.run_time)
        self.run_dir = os.getcwd().replace('\\', '/')

        self.min_path = ('miniatures' + f"_{self.run_time[0]}_{self.run_time[1]}").replace(':', '.')
        if not os.path.exists(self.min_path):
            os.makedirs(self.min_path)

        self.check_box_initialize()
        self.table_widget_initialize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())

# TO DO: написать комментарии. Придумать второе окно, и главное окно. Придумать штуку с тегами.
