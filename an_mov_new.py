import sys
import os
from time import ctime, time, sleep
from vibor_new_dialog_based_other import Ui_MainWindow
import datetime as dt
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QPixmap
from PIL import Image
import sqlite3
import shutil
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractButton
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox, QInputDialog

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


class ViewWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buffered_tag_index = 0
        self.initialize_base()
        self.tableWidget.itemSelectionChanged.connect(self.show_selected_items)
        self.current_selection = []
        self.current_selected_tag_index = 0
        self.min_path = ''
        self.current_image_path = ''
        self.imported_dirs = []
        self.preview_position = 0
        self.formated_infos = []
        self.mode = 'folders'
        self.current_tag_name = ''
        self.current_tag_name_id = 0


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
        self.add_one_tag_button.clicked.connect(self.add_single_image_tag)
        self.add_all_tag_button.clicked.connect(self.add_all_image_tag)
        self.del_one_tag_button.clicked.connect(self.delete_selected_one_image_tag)
        self.del_all_tag_button.clicked.connect(self.delete_selected_all_image_tag)
        self.del_all_tags_of_single_element_button.clicked.connect(self.delete_all_one_image_tags)
        self.del_all_tags_of_all_elements_button.clicked.connect(self.delete_all_all_images_tags)
        self.show_imgs_by_tag_button.clicked.connect(self.show_by_tag)
        self.show_imgs_by_catalog_button.clicked.connect(self.show_by_folder)
        self.leave_out_button.clicked.connect(self.loadout_selections)
        self.run()
        self.showNormal()

    def create_miniature(self, in_path):
        im = Image.open(in_path)
        x, y = im.size
        file_name = in_path.split('/')[-1]
        out_path = self.min_path + '/' + file_name
        # print(out_path)

        im2 = im.resize((x // 3, y // 3))
        # self.log_out_label.setText(f"{out_path} saved")
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

    def go_add_or_not_dialogue_export_add(self):
        valid = QMessageBox.question(
            self, '', "???????????????? ???????????? ?????? ????????????????. ???????????????????? ?????? ??????.",
            QMessageBox.Ok)
        if valid == QMessageBox.Ok:
            pass
    def loadout_selections(self):
        try:
            if not self.current_selection:
                raise ValueError('???????????? ???? ?????????????? ?????? ????????????????. ???????????????? ?????????????????????? ?????? ???????????????? ??????????.')
            paths = list(map(lambda x: x[1], self.current_selection))
            print(paths)
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.Directory)
            # try:
            new_folder_to_out = dialog.getExistingDirectory(self, '?????????????? ???????? ?????? ????????????????.')
            print(new_folder_to_out)
            valid = QMessageBox.question(
                self, '', "?????????????? ?????????? ?????? ???????????????????????????? ?????????????",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                folder_name, ok_pressed = QInputDialog.getText(self, "?????????????? ???????????????? ?????????? ?????? ????????????????",
                                                        "?????????????? ???????????????? ??????????:")
                if ok_pressed:
                    new_folder_to_out = new_folder_to_out + '/' + folder_name
                    if not os.path.exists(new_folder_to_out):
                        os.makedirs(new_folder_to_out)
                    else:
                        raise NameError('?????????? ?????????? ?????? ????????????????????.')

            else:
                print('no ok')
            for _ in paths:
                name = _.split('/')[-1]
                shutil.copy(_, new_folder_to_out + '/' + name)

            self.log_out_label.setText(f'???????????????? ???????????? ?? ?????????? {new_folder_to_out}')
            valid = QMessageBox.question(
                self, '', "???????????? ????????????????.",
                QMessageBox.Ok)
            if valid == QMessageBox.Ok:
                pass


        except ValueError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_export_add()

        except NameError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_export_add()




            # photo_files = list(filter(lambda z: z[1] in PHOTOFORMATS, list(
            #     map(lambda y: [self.dir_name + '/' + y, y.split('.')[-1]],
            #         (filter(lambda x: x[0] != '.' and '.' in x, os.listdir(path=self.dir_name)))))))
            # print(photo_files)


    def show_imgs_preview(self):
        self.preview_size = self.image_label.size()
        self.preview_sizes = (self.preview_size.width(), self.preview_size.height())
        if self.current_selection:
            self.preview_position = self.preview_position % len(self.current_selection)
            self.name_out_label.setText(
                f"{self.preview_position + 1}/{len(self.current_selection)},"
                f" {self.current_selection[self.preview_position][1]}")
            # if self.tag_choose_box.currentIndex() == 0:
            #     self.current_selected_tag_index = self.tag_choose_box.currentIndex()
            # self.tag_choose_box.setCurrentIndex(self.current_selected_tag_index)

            self.cur_im_id = self.current_selection[self.preview_position][0]
            self.current_tags = self.curs.execute(f'''SELECT name from tags WHERE id in (SELECT id_tag from image_tags WHERE id_image = '{self.cur_im_id}')
            ORDER BY id''').fetchall()
            current_tags = list(map(lambda x: x[0], self.current_tags))
            print(current_tags)
            self.tag_name_label.setText(" ????????: " + ', '.join(current_tags))
            self.pixmap = QPixmap(self.current_selection[self.preview_position][-1])
            self.pixmap = self.pixmap.scaled(*self.preview_sizes, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.image_label.setPixmap(self.pixmap)
        # if self.mode == 'tags':
        #     self.table_widget_initialize_tags()

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
            self.log_out_label.setText('?????? ?? ??????????????. ?????????? ????????????????????.')
            return

        if tags_dupped:
            valid = QMessageBox.question(
                self, '', "?????????? ?????????? ???????????????????? ??????????. ???????????? ?????????? ???? ???????????",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                for _ in tags_dupped:
                    self.curs.execute(
                        f'''delete from tags where id = '{_[0]}' 
''').fetchall()
                    self.base_conection.commit()
                    self.initialize_base()
                    self.log_out_label.setText('?????????? ???????? ?????????????? ???? ??????????.')
        elif not tags_dupped:
            self.log_out_label.setText('???????????? ?????? ?? ??????????.')

        if imgs_duped:
            valid = QMessageBox.question(
                self, '', "?????????? ?????????????????????? ???????????????????? ??????????. ???????????? ?????????? ???? ???????????????????????",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                for _ in imgs_duped:
                    self.log_out_label.setText(f"?????????????????????? {_[1]} ??????????????")
                    self.curs.execute(
                        f'''delete from images where id = '{_[0]}' 
            ''').fetchall()
                    self.base_conection.commit()
                    self.initialize_base()
                    self.log_out_label.setText('?????????? ???????? ?????????????? ???? ??????????????????????')
        elif not imgs_duped:
            self.log_out_label.setText('???????????? ?????? ?? ????????????????????????.')
        self.deselect()
        self.initialize_base()
        self.table_widget_initialize_folder()

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
                if self.mode == 'tags':
                    self.table_widget_initialize_tags()
                self.show_imgs_preview()

    def resizeEvent(self, event):
        if self.mode == 'tags':
            self.table_widget_initialize_tags()
        self.show_imgs_preview()

    def add_images_to_base(self, li):
        for ___ in li:
            path, tip, c_date, m_date, mini_path = ___

            self.log_out_label.setText(f"?????????? {''.join(path.split('/')[:-1])} ??????????????????")
            self.curs.execute(f'''INSERT INTO images (path, type, modified_date, creation_date, mini_path)
            VALUES ('{path}', '{tip}', '{c_date}', '{m_date}', '{mini_path}')''').fetchall()
            self.base_conection.commit()
        self.initialize_base()

    def go_add_or_not_dialogue_folder_add(self):
        valid = QMessageBox.question(
            self, '', "???????????????? ???????????? ?????? ???????????????????? ??????????. ?????????????????????? ?????? ???????",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.add_folder()

    def go_add_or_not_dialogue_image_add(self):
        valid = QMessageBox.question(
            self, '', "???????????????? ???????????? ?????? ???????????????????? ??????????????????????(????). ?????????????????????? ?????? ???????",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.add_image()

    def go_add_or_not_dialogue_tag_add(self):
        valid = QMessageBox.question(
            self, '', "???????????????? ???????????? ?????? ???????????????????? ????????. ???????????????????? ?????? ??????.",
            QMessageBox.Ok)
        if valid == QMessageBox.Ok:
            pass

    def add_folder(self):
        self.deselect()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        try:
            self.dir_name = dialog.getExistingDirectory(self, '?????????????? ???????? ?? ?????????? ?? ??????????????????????????')
            photo_files = list(filter(lambda z: z[1] in PHOTOFORMATS, list(
                map(lambda y: [self.dir_name + '/' + y, y.split('.')[-1]],
                    (filter(lambda x: x[0] != '.' and '.' in x, os.listdir(path=self.dir_name)))))))
            print(photo_files)

            if not photo_files:
                raise ImportError('?? ?????????? ?????? ??????????????????????. ???????????????? ?????????? ?? ??????????????????????????.')
            if self.images:
                imgs_duped = list(filter(lambda x: x in list(map(lambda z: z[1], self.images)),
                                         list(map(lambda x: x[0], photo_files))))
                print(imgs_duped)
                if imgs_duped == photo_files:
                    raise DupeError('?????? ?????????????????????? ?? ?????????? ?????? ??????????????????.')
                else:
                    photo_files = list(filter(lambda x: x[0] not in imgs_duped, photo_files))

            for _ in photo_files:
                o_p = self.create_miniature(_[0])
                file_stat = os.stat(_[0])
                _.extend([get_formated_date(file_stat.st_mtime), get_formated_date(file_stat.st_ctime), o_p])

            self.formated_infos = photo_files
            self.add_images_to_base(self.formated_infos)
            self.table_widget_initialize_folder()

        except FileNotFoundError:
            self.log_out_label.setText('?????????????????????? ?????????????? ???????????????????? ?????????? ?? ??????????????????????????')
            self.go_add_or_not_dialogue_folder_add()

        except ImportError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_folder_add()

        except DupeError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_folder_add()


    def add_tag(self):
        try:
            tag_name = self.tag_name_edit.text()
            if tag_name == '':
                raise ValueError('?????? ???????? ???? ??????????????.')
            tag_names = list(map(lambda x: x[1], self.tags))
            if tag_name not in tag_names:
                self.tag_name_edit.setText('')
                self.log_out_label.setText(f"?????? {tag_name} ????????????????")
                self.curs.execute(f'''INSERT INTO tags (name)
        VALUES ('{tag_name}');''').fetchall()
                self.base_conection.commit()
                self.initialize_base()
            else:
                raise DupeError('?????? ?? ?????????? ???????????? ?????? ????????????????????. ???? ???? ?????? ????????????????.')
        except DupeError as exeption:
            self.log_out_label.setText(str(exeption))
            self.tag_name_edit.setText('')
            self.go_add_or_not_dialogue_tag_add()
        except ValueError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_tag_add()

        self.initialize_base()

    def show_by_folder(self):
        self.mode = 'folders'
        self.current_tag_name = ''
        self.current_tag_name_id = 0
        self.table_widget_initialize_folder()

    def show_by_tag(self):
        self.mode = 'tags'
        tag_name = self.tag_choose_box.currentText()
        tag_index_in_tags = self.curs.execute(f'''
                SELECT id from tags WHERE name = '{tag_name}'
                ''').fetchall()[0][0]
        self.current_tag_name = tag_name
        self.current_tag_name_id = tag_index_in_tags
        self.table_widget_initialize_tags()

    def add_image(self):
        self.deselect()
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)
        try:
            image_path = dialog.getOpenFileNames(self, '?????????????? ???????? ?? ??????????????????????(????)')[0]
            if len(image_path) == 1:
                # for _ in image_path:
                #     print(_)
                # photo_files = list(map(lambda x: x[0], image_path))
                photo_files = list(map(lambda u: u, list(filter(lambda z: z[1] in PHOTOFORMATS, list(
                    map(lambda y: [y, y.split('.')[-1]],
                        (filter(lambda x: x[0] != '.' and '.' in x, image_path))))))))
                print(photo_files)
            else:
                photo_files = list(filter(lambda z: z[1] in PHOTOFORMATS, list(
                    map(lambda y: [y, y.split('.')[-1]],
                        (filter(lambda x: x[0] != '.' and '.' in x, image_path))))))
                print(photo_files)
            #
            if not photo_files:
                raise ImportError('?????????????????? ???????? ???? ???????????????? ????????????????????????(??????).')

            if self.images:
                if len(photo_files) == 1:
                    imgs_duped = list(filter(lambda x: x in list(map(lambda z: z[1], self.images)), list(map(lambda x: x, photo_files[0]))))
                    print(imgs_duped)
                    if imgs_duped[0] == photo_files[0][0]:
                        raise DupeError('?????????????????? ???????? ?????? ????????????????(??).')

                    else:
                        photo_files = list(filter(lambda x: x[0] not in imgs_duped, photo_files))
                else:
                    imgs_duped = list(filter(lambda x: x in list(map(lambda z: z[1], self.images)), list(map(lambda x: x[0], photo_files))))
                    print(imgs_duped)
                    if imgs_duped[0] == photo_files[0][0]:
                        raise DupeError('?????????????????? ???????? ?????? ????????????????(??).')

                    else:
                        photo_files = list(filter(lambda x: x[0] not in imgs_duped, photo_files))

            #             else:
            #                 photo_files = list(filter(lambda x: x not in imgs_duped, photo_files))
            #
            for _ in photo_files:
                # photo_files = list(filter(lambda x: x not in imgs_duped, photo_files))
                path = _[0]
                o_p = self.create_miniature(path)
                file_stat = os.stat(path)
                _.extend([get_formated_date(file_stat.st_mtime), get_formated_date(file_stat.st_ctime), o_p])



            self.formated_infos = photo_files
            self.add_images_to_base(self.formated_infos)
            self.log_out_label.setText("?????????????????????? ??????????????????.")
            self.table_widget_initialize_folder()

        except FileNotFoundError:
            self.log_out_label.setText('?????????????????????? ???????????? ???????? ?? ??????????????????????(????)')
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
                self.base_path = dialog.getOpenFileName(self, '???????????????? ???????? ?? ????????')[0]
                if self.base_path == '':
                    raise ValueError('???????? ?? ???????? ???? ????????????')
                elif self.base_path.split('.')[-1] != 'sqlite':
                    raise AttributeError('???????????? ???????? ???????????? ??????????????????????')
                print(f'???????? ?? ???????? ???????????? {self.base_path}')
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
        image_tags_duples_ids = []
        all_im_tags = []
        for _ in self.image_tags:
            curr_tup_datas = (_[1], _[2])
            if curr_tup_datas not in all_im_tags:
                all_im_tags.append(curr_tup_datas)
            else:
                image_tags_duples_ids.append(_[0])
        if image_tags_duples_ids:
            for __ in image_tags_duples_ids:
                self.curs.execute(f'''
                DELETE FROM image_tags WHERE id = '{__}'
''').fetchall()
                self.base_conection.commit()


        self.check_box_initialize()

    def add_single_image_tag(self, mode=False):
        try:
            unformated_selection = list(map(lambda x: x.text(), self.tableWidget.selectedItems()))
            formated_selection = []
            for _ in range(0, len(unformated_selection), 6):
                formated_selection.append(unformated_selection[_:_ + 6])
            if not mode:
                current_image = formated_selection[self.preview_position]
                current_tag = self.tag_choose_box.currentText()
                print(current_image)
                im_id = current_image[0]
                print(current_tag)
                print(im_id)
                tag_id = self.curs.execute(f'''SELECT id FROM tags WHERE id = (SELECT id WHERE name = '{current_tag}')
                ''').fetchall()[0][0]
                print(tag_id)
                dupples_id = []
                all_im_tags = []
                imgs_tups = list(map(lambda x: (x[1], x[2]), self.image_tags))
                print(imgs_tups)
                if (int(im_id), tag_id) not in imgs_tups:
                    self.curs.execute(f'''INSERT INTO image_tags (id_image, id_tag)
                    VALUES (?, ?)
                    ''', (im_id, tag_id)).fetchall()
                    self.base_conection.commit()
                    self.log_out_label.setText(f'?????? {current_tag} ?????? ????????????????????.')
                else:
                    raise DupeError('?????? ?????? ?????? ????????????????.')


                # if not dupple_tags:
                # else:


            else:
                current_tag = self.tag_choose_box.currentText()
                tag_id = self.curs.execute(f'''SELECT id FROM tags WHERE id = (SELECT id WHERE name = '{current_tag}')
                        ''').fetchall()[0][0]
                print(tag_id)
                goodie_im_tags = []
                for _ in formated_selection:
                    print(_)
                    im_id = _[0]
                    print(current_tag)
                    print(im_id)
                    imgs_tups = list(map(lambda x: (x[1], x[2]), self.image_tags))
                    print(imgs_tups)
                    unduped_pairs = list(filter(lambda x: x == (int(im_id), tag_id), imgs_tups))
                    print(unduped_pairs)
                    if not unduped_pairs:
                        goodie_im_tags.append((int(im_id), tag_id))
                print(goodie_im_tags)
                if goodie_im_tags:
                    for _ in goodie_im_tags:
                        cur_im_id, cur_tag_id = _
                    # if (int(im_id), tag_id) not in imgs_tups:
                        self.curs.execute(f'''INSERT INTO image_tags (id_image, id_tag)
                                        VALUES (?, ?)
                                        ''', (cur_im_id, cur_tag_id)).fetchall()
                        self.base_conection.commit()
                    self.log_out_label.setText(f'?????? {current_tag} ?????? ???????????????????? ?? ??????????????????????.')
                else:
                    raise DupeError('???????? ?????? ???????? ??????????????????.')

                    # self.curs.execute(f'''INSERT INTO image_tags (id_image, id_tag)
                    #             VALUES (?, ?)
                    #         ''', (im_id, tag_id)).fetchall()
                    # self.base_conection.commit()

            self.log_out_label.setText('???????? ???????? ??????????????????????.')
            self.initialize_base()
            self.show_imgs_preview()
        except DupeError as exeption:
            self.log_out_label.setText(str(exeption))
            self.go_add_or_not_dialogue_tag_add()

    def add_all_image_tag(self):
        self.add_single_image_tag(mode=True)

    def delete_selected_one_image_tag(self, mode=False):
        self.box_choosen_tag = self.tag_choose_box.currentText()
        self.box_choosen_tag_id = self.curs.execute(f'''
                            SELECT id from tags WHERE id = (SELECT id FROM tags WHERE name = '{self.box_choosen_tag}')            
                            ''').fetchall()[0][0]
        print(self.box_choosen_tag_id)
        unformated_selection = list(map(lambda x: x.text(), self.tableWidget.selectedItems()))
        formated_selection = []
        for _ in range(0, len(unformated_selection), 6):
            formated_selection.append(unformated_selection[_:_ + 6])
        if not mode:
            current_image = self.cur_im_id
            current_tag = self.tag_choose_box.currentText()
            print(current_image)
            self.curs.execute(f'''
            DELETE FROM image_tags WHERE id_image = '{self.cur_im_id}' AND id_tag = '{self.box_choosen_tag_id}'
            ''')
            self.base_conection.commit()
            self.log_out_label.setText(f'?????? {current_tag} ?????? ????????????.')
        else:
            for _ in formated_selection:
                current_image_id = _[0]
                current_tag = self.tag_choose_box.currentText()
                print(current_image_id)
                # print(self.curr_tag_id)
                self.curs.execute(f'''
                            DELETE FROM image_tags WHERE id_image = '{current_image_id}' AND id_tag = '{self.box_choosen_tag_id}'
                            ''')
                self.base_conection.commit()
                self.log_out_label.setText(f'?????? {current_tag} ?????? ???????????? ???? ???????? ??????????????????.')

        self.initialize_base()
        self.repair_autoincrement()
        if self.mode == 'tags':
            self.table_widget_initialize_tags()
        self.show_imgs_preview()

    def delete_selected_all_image_tag(self):
        self.delete_selected_one_image_tag(True)

    def delete_all_one_image_tags(self, mode=False):
        if not mode:
            selected_im = self.current_selection[self.preview_position]
            im_id = selected_im[0]
            self.curs.execute(f'''
                                        DELETE from image_tags WHERE id_image = '{im_id}'
                                        ''').fetchall()
            self.log_out_label.setText(f'?????? ???????? ???????????????? ???????? ??????????????.')


        else:
            for _ in self.current_selection:
                im_id = _[0]
                self.curs.execute(f'''
                            DELETE from image_tags WHERE id_image = '{im_id}'
                            ''').fetchall()
            self.log_out_label.setText(f'?????? ???????? ???????? ?????????????????? ???????? ??????????????.')

        self.base_conection.commit()
        self.initialize_base()
        self.repair_autoincrement()
        if self.mode == 'tags':
            self.table_widget_initialize_tags()
        self.show_imgs_preview()

    def delete_all_all_images_tags(self):
        self.delete_all_one_image_tags(mode=True)

    def delete_tag(self):
        self.initialize_base()
        tag_name = self.tag_choose_box.currentText()
        valid = QMessageBox.question(
            self, '', f"?????????????????????????? ?????????????? ?????? {tag_name}?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.log_out_label.setText(f"?????? {tag_name} ????????????")
            self.curs.execute(
                f'''delete from tags where id = (SELECT id from tags where name = '{tag_name}')''').fetchall()
            self.base_conection.commit()
            tag_index_in_tags = list(map(lambda x: x[1], self.tags)).index(tag_name)
            new_tags = self.tags
            new_tags.pop(tag_index_in_tags)
            self.tags = new_tags
            self.tag_deleted = True

            self.curs.execute(f'''
            DELETE FROM image_tags WHERE id_tag = '{tag_index_in_tags}'
            ''').fetchall()
            self.base_conection.commit()

            self.initialize_base()
            self.repair_autoincrement()
            if self.mode == 'tags':
                self.table_widget_initialize_tags()
            else:
                self.table_widget_initialize_folder()

    def delete_image(self):
        unformated_selection = list(map(lambda x: x.text(), self.tableWidget.selectedItems()))
        print(unformated_selection)
        formated_selection = []
        for _ in range(0, len(unformated_selection), 6):
            formated_selection.append(unformated_selection[_:_ + 6])
        print(formated_selection)
        valid = QMessageBox.question(
            self, '', f"?????????????????????????? ?????????????? ?????? ??????????????????????(??)?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            for _ in formated_selection:
                print(_)
                if os.path.exists(_[-1]):
                    os.remove(_[-1])
                self.curs.execute(f'''delete from images where id = '{_[0]}'
                ''').fetchall()
                self.base_conection.commit()
            if len(formated_selection) == len(self.images):
                self.tableWidget.clear()
                self.current_selection = []
                self.tableWidget.setColumnCount(0)
                self.tableWidget.setRowCount(0)
            self.initialize_base()
            self.repair_autoincrement()
            self.table_widget_initialize_folder()
            self.deselect()
            if not self.images:
                self.log_out_label.setText('?????????????????????? ???????? ??????????????.')
                sleep(1.0)
                self.dupe_check_button.setEnabled(False)
                self.log_out_label.setText('???????? ?????????????????????? ??????????. ???????????????? ??????????????????????(??).')
            else:
                self.log_out_label.setText('?????????????????????? ???????? ??????????????.')

    def deselect(self):
        self.tableWidget.clearSelection()
        self.name_out_label.setText('')
        self.preview_position = 0
        self.tag_name_label.setText('????????:')
        self.image_label.clear()
        self.navigation_tagging_checking_buttons_state_initialize()
        # if self.mode == 'tags':
        #     self.table_widget_initialize_tags()

    def navigation_tagging_checking_buttons_state_initialize(self):
        if self.current_selection:
            if len(self.current_selection) == 1:
                for _ in self.navigation_arrows_button_group.buttons():
                    _.setEnabled(True)
                for _ in self.single_selection_button_group.buttons():
                    _.setEnabled(True)
                for _ in self.multi_selection_button_group.buttons():
                    _.setEnabled(False)
                for _ in self.selected_manipulations_button_group.buttons():
                    _.setEnabled(True)

            else:
                for _ in self.navigation_arrows_button_group.buttons():
                    _.setEnabled(True)
                for _ in self.single_selection_button_group.buttons():
                    _.setEnabled(True)
                for _ in self.multi_selection_button_group.buttons():
                    _.setEnabled(True)
                for _ in self.selected_manipulations_button_group.buttons():
                    _.setEnabled(True)

        else:
            for _ in self.navigation_arrows_button_group.buttons():
                _.setEnabled(True)
            for _ in self.single_selection_button_group.buttons():
                _.setEnabled(False)
            for _ in self.multi_selection_button_group.buttons():
                _.setEnabled(False)
            for _ in self.selected_manipulations_button_group.buttons():
                _.setEnabled(True)

    def check_box_initialize(self):
        self.current_selected_tag_text = self.tag_choose_box.currentText()
        if self.current_selected_tag_text and not self.tag_deleted:
            self.current_selected_tag_index = self.tags.index(list(filter(lambda x: self.current_selected_tag_text in x[1], self.tags))[0])
        else:
            self.current_selected_tag_index = 0
            self.tag_deleted = False
        print(self.current_selected_tag_text)
        self.tag_choose_box.clear()
        if self.tags:
            self.tag_choose_box.setEnabled(True)
            self.delete_tag_button.setEnabled(True)
            if len(self.tags) > 1:
                buff_tags = self.tags
                new_tags = [self.tags[self.current_selected_tag_index]]
                buff_tags.pop(buff_tags.index(new_tags[0]))
                new_tags.extend(buff_tags)
                for _ in new_tags:
                    self.tag_choose_box.addItem(_[1])
            else:
                self.tag_choose_box.addItem(self.tags[0][1])

        else:
            self.tag_choose_box.setEnabled(False)
            self.delete_tag_button.setEnabled(False)

    def table_widget_initialize_folder(self):
        self.mode = 'folders'
        res = self.curs.execute("SELECT * from images").fetchall()
        if not res:
            self.name_out_label.setText('?????????????????????? ???? ??????????????. ???????????????? ??????????????????????.')
            self.dupe_check_button.setEnabled(False)
            # self.add_folder()
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

    def table_widget_initialize_tags(self):
        res = self.curs.execute(f'''
        SELECT * FROM images WHERE id in (SELECT id_image FROM image_tags WHERE id_tag = '{self.current_tag_name_id}')''').fetchall()
        if not res:
            self.name_out_label.setText('?????????????????????? ???? ???????? ???? ??????????????.')
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.dupe_check_button.setEnabled(False)
            self.deselect()
            # self.add_folder()
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

        elif self.tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM tags) - 1 WHERE name = 'tags'
            ''').fetchall()
            self.base_conection.commit()

        if not self.images:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'images'
            ''').fetchall()
            self.base_conection.commit()

        elif self.images:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM images) - 1 WHERE name = 'images'
            ''').fetchall()
            self.base_conection.commit()

        if not self.image_tags:
            self.curs.execute('''UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'image_tags'
            ''').fetchall()
            self.base_conection.commit()

        elif self.image_label:
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

        # self.check_box_initialize()
        self.table_widget_initialize_folder()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ViewWindow()
    ex.show()
    sys.exit(app.exec_())

# TO DO: ???????????????? ??????????????????????. ?????????????????? ???????????? ????????, ?? ?????????????? ????????. ?????????????????? ?????????? ?? ????????????.
