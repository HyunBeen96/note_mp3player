import os
import sys
import importlib
from PyQt5.QtWidgets import *     # GUI 위젯 클래스들
from PyQt5.QtGui import *         # 폰트, 커서 등 그래픽 관련
from PyQt5.QtCore import *        # 타이머, 애니메이션 등 핵심 기능
from PyQt5 import uic             # UI 파일을 로드할 수 있는 모듈

# Qt Designer로 만든 .ui 파일을 불러와서 Python 클래스 형태로 변환합니다.
form_class = uic.loadUiType("./QtNotepad.ui")[0]

# 메인 윈도우 클래스 정의. QMainWindow와 form_class(디자인) 상속.
class ExampleApp(QMainWindow, form_class):
    MARGIN = 6  # 마우스로 resize 가능한 테두리 범위(px)

    def __init__(self):
        super().__init__()  # 부모 클래스 초기화
        self.setupUi(self)  # UI 연결
        self.setWindowTitle('Qt Note Pad')  # 윈도우 타이틀 설정

        # ✅test
        # 크기 조절 상태 변수
        self._resizing = False
        self._resize_dir = None


        self.menuBar().installEventFilter(self)
        self._drag_pos = None
        self._dragging = False

        # # ✅메뉴바를 초기에 보이지 않도록 숨김 (높이 0으로 설정)
        # self.menuBar().setFixedHeight(0)
        # self.menu_visible = False  # 메뉴바 표시 여부를 추적하는 플래그
        #
        # # ✅메뉴바에 대한 애니메이션 설정
        # self.menu_anim = QPropertyAnimation(self.menuBar(), b"maximumHeight")
        # self.menu_anim.setDuration(200)  # 메뉴 애니메이션 지속 시간 (밀리초 단위)
        #
        # # ✅마우스 위치를 주기적으로 체크하기 위한 타이머 설정
        # self.mouse_timer = QTimer(self)
        # self.mouse_timer.setInterval(100)  # 0.1초마다 위치 확인
        # self.mouse_timer.timeout.connect(self.check_mouse_position)  # 타이머와 메서드 연결
        # self.mouse_timer.start()

        # ✅plainTextEdit 위젯의 객체 이름을 간단히 참조
        editor = self.plain_te

        # ✅파일 메뉴의 각 액션을 기능에 연결
        self.actionOpen.triggered.connect(self.open_file)        # 열기
        self.actionSave.triggered.connect(self.save_file)        # 저장
        self.actionSave_as.triggered.connect(self.save_file_as)  # 다른 이름으로 저장
        self.actionExit.triggered.connect(self.close)            # 종료
        self.actionNew.triggered.connect(self.new_file)          # 새 문서

        # ✅편집 메뉴 기능 연결
        self.actionUndo.triggered.connect(editor.undo)           # 실행 취소
        self.actionRedo.triggered.connect(editor.redo)           # 다시 실행
        self.actionCut.triggered.connect(editor.cut)             # 잘라내기
        self.actionCopy.triggered.connect(editor.copy)           # 복사
        self.actionPaste.triggered.connect(editor.paste)         # 붙여넣기
        self.actionSelect_All.triggered.connect(editor.selectAll) # 전체 선택
        self.actionFont.triggered.connect(self.change_font)      # 글꼴 변경
        self.actionDelete.triggered.connect(self.delete_text)    # 텍스트 삭제
        self.actionTheme.triggered.connect(self.choose_custom_theme)

        # ✅도움말 메뉴 연결
        self.actionAbout.triggered.connect(self.show_about)      # 정보창

        # ✅현재 열려 있는 파일 경로 저장 변수
        self.current_file = None

        # ✅창 제목을 현재 상태에 맞게 업데이트
        self.update_window_title()

        # ✅ 프레임리스 적용
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 배경 투명하게
        # 메뉴바 우측에 커스텀 버튼들 추가
        btn_min = QPushButton()
        btn_max = QPushButton()
        btn_close = QPushButton()
        # 시스템 스타일 기본 아이콘 불러오기
        btn_min.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarMinButton))
        btn_max.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        btn_close.setIcon(QApplication.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        btn_min.setIconSize(QSize(8, 8))  # 너가 원하는 크기로 조절
        btn_max.setIconSize(QSize(8, 8))  # 너가 원하는 크기로 조절
        btn_close.setIconSize(QSize(8, 8))  # 너가 원하는 크기로 조절




        btn_min.setObjectName("TitleButton")
        btn_max.setObjectName("TitleButton")
        btn_close.setObjectName("TitleButton")


        for btn in [btn_min, btn_max, btn_close]:
            btn.setFixedSize(24, 24)

        corner_widget = QWidget()
        layout = QHBoxLayout(corner_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(btn_min)
        layout.addWidget(btn_max)
        layout.addWidget(btn_close)
        self.menuBar().setCornerWidget(corner_widget, Qt.TopRightCorner)
        # 버튼 기능 연결
        btn_min.clicked.connect(self.showMinimized)
        def toggle_max_restore():
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        btn_max.clicked.connect(toggle_max_restore)
        btn_close.clicked.connect(self.close)


        # ✅깔맞춤 테마
        self.base_theme_template = """
        QWidget {
            background-color: {{MAIN_BG}};
            border-radius: 5px;
        }

        QMenuBar {
            background-color: {{MENU_BG}};
            color: #333;
            font-weight: bold;
            border: none;
        }

        QMenuBar::item {
            background: transparent;
            padding: 5px 15px;
        }

        QMenuBar::item:selected {
            background: {{MENU_SELECTED}};
            color: white;
        }

        QMenu {
            background-color: {{MENU_DROPDOWN}};
            color: #333;
        }

        QMenu::item:selected {
            background-color: {{MENU_HOVER}};
            color: black;
        }

        QPlainTextEdit {
            background-color: rgba(255, 255, 255, 210);
            border: 1px solid {{EDIT_BORDER}};
            border-radius: 6px;
            padding: 10px;
            color: #222;
            font-family: "맑은 고딕", sans-serif;
            font-size: 13px;
        }

        QToolBar {
            background-color: {{MENU_BG}};  /* 메뉴바와 동일하게 */
            spacing: 4px;
            padding: 4px;
            margin: 0px;
            border: none;
        }

        QStatusBar {
            background-color: transparent;
            margin: 0px;
            padding: 2px;
            color: #444;
        }

        QMessageBox {
            background-color: white;
            color: black;
            border-radius: 6px;
        }

        QMessageBox QLabel {
            background-color: transparent;
            color: black;
        }

        /* ✅ 일반 버튼 */
        QPushButton {
            background-color: {{BTN_BG}};
            border: 1px solid {{BTN_BORDER}};
            border-radius: 6px;
            padding: 6px 12px;
            color: black;
        }

        QPushButton:hover {
            background-color: {{BTN_HOVER}};
            color: white;
        }

        /* ✅ 타이틀바 버튼 (min/max/close) - 메뉴바 버튼 스타일로 */
        QPushButton#TitleButton {
            background-color: {{MENU_BG}};  /* 메뉴바와 완전 일치하게 */
            border: none;
            padding: 4px 8px;
            color: #222;
            font-size: 12px;
            font-weight: normal;
            border-radius: 0px;
        }

        QPushButton#TitleButton:hover {
            background: {{MENU_SELECTED}};
            color: white;
        }


        QMessageBox QPushButton {
            background-color: {{MSG_BTN}};
            border: 1px solid {{BTN_BORDER}};
            border-radius: 4px;
            padding: 5px 10px;
            color: #222;
            font-weight: bold;
        }

        QMessageBox QPushButton:hover {
            background-color: {{MSG_BTN_HOVER}};
            color: black;
        }
        QToolButton {
            background-color: transparent;
            border: none;
            padding: 2px;
            margin: 0px;
        }

        QToolButton:hover {
            background-color: rgba(150, 160, 255, 40);  /* 살짝 하이라이트 효과 */
            border-radius: 16px;
        }
        """

        self.load_widgets_and_bind_menu()







    # ✅파일 열기 기능 구현
    def open_file(self):
        if self.plain_te.document().isModified():
            reply = QMessageBox.question(
                self,
                "변경 내용 저장",
                "현재 문서를 저장하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return  # 열기 취소

        fname, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                self.plain_te.setPlainText(f.read())
            self.current_file = fname
            self.update_window_title()

    # ✅파일 저장 기능
    def save_file(self):
        if self.current_file:  # 기존에 열려 있는 파일이 있을 경우
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.plain_te.toPlainText())  # 현재 텍스트 저장
            self.plain_te.document().setModified(False)
        else:  # 새 문서인 경우
            self.save_file_as()

    # ✅'다른 이름으로 저장' 기능
    def save_file_as(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(self.plain_te.toPlainText())  # 내용 저장
            self.current_file = fname
            self.plain_te.document().setModified(False)
            self.update_window_title()  # 제목 업데이트

    # ✅글꼴 변경 대화상자
    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.plain_te.setFont(font)  # 사용자가 선택한 글꼴 적용

    # ✅프로그램 정보창 표시
    def show_about(self):
        QMessageBox.information(self, "About", "Qt Notepad\nMade with PyQt5")
        #QMessageBox.about(self, 'Qt Note Pad',
        #                  '만든이 : ABC Lab\n\r버전 정보 : 1.0.0.0')

    # ✅텍스트 삭제 기능
    def delete_text(self):
        if not self.plain_te:
            return

        cursor = self.plain_te.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()  # 선택된 텍스트 삭제
        else:
            cursor.deleteChar()  # 선택이 없으면 커서 위치 문자 삭제
        self.plain_te.setTextCursor(cursor)  # 커서 상태 업데이트

    # ✅새 파일 생성 (기존 내용 저장 여부 확인 포함)
    def new_file(self):
        if self.plain_te.document().isModified():
            reply = QMessageBox.question(
                self,
                "변경 내용 저장",
                "현재 문서를 저장하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                success = self.save_file()
                if not success:
                    return  # 저장 취소했으니 원복
            elif reply == QMessageBox.Cancel:
                return

        # 여기부터는 진짜 저장 완료됐을 때만 실행
        self.plain_te.clear()
        self.current_file = None
        self.update_window_title()

    # ✅윈도우 타이틀을 현재 파일 이름으로 설정
    def update_window_title(self):
        if self.current_file:
            filename = self.current_file.split("/")[-1]  # 경로를 제외한 파일 이름 추출
        else:
            filename = "제목없음"

        self.setWindowTitle(f"{filename} - Qt Note Pad")

    # ✅마우스 위치 감지하여 메뉴바 보이거나 숨기기
    def check_mouse_position(self):
        pos = self.mapFromGlobal(QCursor.pos())

        if pos.y() <= 10:
            self.show_menu_bar()
        elif pos.y() > 50:
            # 메뉴가 열려있으면 메뉴바 유지
            if QApplication.activePopupWidget() is None:
                self.hide_menu_bar()

    # ✅메뉴바 보이기 애니메이션 실행
    def show_menu_bar(self):
        if not self.menu_visible:
            self.menu_visible = True
            self.menu_anim.stop()
            self.menu_anim.setStartValue(0)
            self.menu_anim.setEndValue(30)  # 보일 때 높이 설정
            self.menu_anim.start()

    # ✅메뉴바 숨기기 애니메이션 실행
    def hide_menu_bar(self):
        if self.menu_visible:
            if QApplication.activePopupWidget() is not None:
                return  # 메뉴가 열려 있으면 숨기지 않음
            self.menu_visible = False
            self.menu_anim.stop()
            self.menu_anim.setStartValue(30)
            self.menu_anim.setEndValue(0)
            self.menu_anim.start()

    # ✅종료 이벤트 설정
    def closeEvent(self, event):
        if self.plain_te.document().isModified():
            reply = QMessageBox.question(
                self,
                "변경 내용 저장",
                "변경된 내용을 저장하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.save_file()
                event.accept()  # 종료 진행
            elif reply == QMessageBox.No:
                event.accept()  # 종료 진행
            else:  # Cancel
                event.ignore()  # 종료 취소
        else:
            event.accept()

    def eventFilter(self, obj, event):
        if obj == self.menuBar():
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._dragging = True
                    self._offset = event.globalPos() - self.frameGeometry().topLeft()
            elif event.type() == QEvent.MouseMove:
                if self._dragging:
                    if QApplication.mouseButtons() & Qt.LeftButton:  # 실제 눌려있는지 확인
                        self.move(event.globalPos() - self._offset)
                    else:
                        self._dragging = False  # 눌려있지 않으면 드래그 해제
            elif event.type() == QEvent.MouseButtonRelease:
                self._dragging = False
        return super().eventFilter(obj, event)

    def choose_custom_theme(self):
        base_color = QColorDialog.getColor(title="기본 테마 색상 선택")
        if not base_color.isValid():
            return

        def hex(c: QColor): return c.name()

        def alpha(c: QColor, a): return f"rgba({c.red()}, {c.green()}, {c.blue()}, {a})"

        base = base_color.lighter(115)  # 전체적으로 한 단계 밝게 시작

        bg = alpha(base, 210)  # 전체 배경 - 적당히 투명
        menu = alpha(base, 160)  # 메뉴바 - 좀 더 연함
        menu_selected = alpha(base_color.darker(110), 180)
        menu_dropdown = alpha(base.lighter(120), 220)
        menu_hover = alpha(base.lighter(110), 190)
        edit_border = alpha(base_color.darker(110), 100)

        btn_bg = alpha(base, 120)  # 버튼 기본색
        btn_hover = alpha(base.lighter(110), 160)
        btn_border = alpha(base_color.darker(120), 80)

        msg_btn = alpha(base.lighter(105), 150)
        msg_btn_hover = alpha(base.lighter(110), 200)

        themed_qss = self.base_theme_template \
            .replace("{{MAIN_BG}}", bg) \
            .replace("{{MENU_BG}}", menu) \
            .replace("{{MENU_SELECTED}}", menu_selected) \
            .replace("{{MENU_DROPDOWN}}", menu_dropdown) \
            .replace("{{MENU_HOVER}}", menu_hover) \
            .replace("{{EDIT_BORDER}}", edit_border) \
            .replace("{{BTN_BG}}", btn_bg) \
            .replace("{{BTN_BORDER}}", btn_border) \
            .replace("{{BTN_HOVER}}", btn_hover) \
            .replace("{{MSG_BTN}}", msg_btn) \
            .replace("{{MSG_BTN_HOVER}}", msg_btn_hover)

        self.setStyleSheet(themed_qss)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()
            self._resize_dir = self._get_resize_direction(event.pos())
            if self._resize_dir:
                self._resizing = True
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._resize_dir:
            self._resize_window(event.globalPos())
        else:
            self._update_cursor(event.pos())

    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._resize_dir = None
        super().mouseReleaseEvent(event)

    def _update_cursor(self, pos):
        direction = self._get_resize_direction(pos)
        cursors = {
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'topleft': Qt.SizeFDiagCursor,
            'topright': Qt.SizeBDiagCursor,
            'bottomleft': Qt.SizeBDiagCursor,
            'bottomright': Qt.SizeFDiagCursor
        }
        self.setCursor(cursors.get(direction, Qt.ArrowCursor))

    def _get_resize_direction(self, pos):
        x, y, w, h, m = pos.x(), pos.y(), self.width(), self.height(), self.MARGIN
        if x <= m and y <= m:
            return 'topleft'
        elif x >= w - m and y <= m:
            return 'topright'
        elif x <= m and y >= h - m:
            return 'bottomleft'
        elif x >= w - m and y >= h - m:
            return 'bottomright'
        elif x <= m:
            return 'left'
        elif x >= w - m:
            return 'right'
        elif y <= m:
            return 'top'
        elif y >= h - m:
            return 'bottom'
        return None

    def _resize_window(self, global_pos):
        diff = global_pos - self._drag_pos
        geom = self.geometry()

        if 'left' in self._resize_dir:
            geom.setLeft(geom.left() + diff.x())
        if 'right' in self._resize_dir:
            geom.setRight(geom.right() + diff.x())
        if 'top' in self._resize_dir:
            geom.setTop(geom.top() + diff.y())
        if 'bottom' in self._resize_dir:
            geom.setBottom(geom.bottom() + diff.y())

        self.setGeometry(geom)
        self._drag_pos = global_pos

    # QWidget의 paintEvent 오버라이드해서 둥근 배경을 그림
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        bg_color = QColor(255, 255, 255, 240)  # 원하는 배경 색상
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)

        radius = 5  # 둥글기 정도 (픽셀 단위)
        painter.drawRoundedRect(rect, radius, radius)

    def load_widgets_and_bind_menu(self):
        widget_dir = "widgets"
        for file in os.listdir(widget_dir):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                file_path = os.path.join(widget_dir, file)

                action = QAction(module_name, self)
                self.menuWidgets.addAction(action)

                def create_and_dock_widget(file_path=file_path, module_name=module_name):
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, "create_widget"):
                        widget = module.create_widget()

                        dock = QDockWidget(module_name, self)
                        dock.setWidget(widget)
                        dock.setObjectName(f"dock_{module_name}")
                        dock.setWindowTitle(f"{module_name} 위젯")
                        self.addDockWidget(Qt.RightDockWidgetArea, dock)

                action.triggered.connect(create_and_dock_widget)



# 프로그램의 진입점. 실제로 GUI 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)    # 앱 객체 생성
    main_window = ExampleApp()      # 메인 윈도우 객체 생성
    main_window.show()              # 메인 윈도우 표시
    sys.exit(app.exec_())           # 이벤트 루프 진입 (종료 시 시스템 종료)
