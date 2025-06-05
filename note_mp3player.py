# 기본적인 시스템 모듈과 PyQt5 관련 모듈들을 불러옵니다.
import sys
from PyQt5.QtWidgets import *     # GUI 위젯 클래스들
from PyQt5.QtGui import *         # 폰트, 커서 등 그래픽 관련
from PyQt5.QtCore import *        # 타이머, 애니메이션 등 핵심 기능
from PyQt5 import uic             # UI 파일을 로드할 수 있는 모듈

# Qt Designer로 만든 .ui 파일을 불러와서 Python 클래스 형태로 변환합니다.
form_class = uic.loadUiType("./QtNotepad.ui")[0]

# 메인 윈도우 클래스 정의. QMainWindow와 form_class(디자인) 상속.
class ExampleApp(QMainWindow, form_class):
    def __init__(self):
        super().__init__()  # 부모 클래스 초기화
        self.setupUi(self)  # UI 연결
        self.setWindowTitle('Qt Note Pad')  # 윈도우 타이틀 설정

        # 타이틀 바 제거 및 투명 배경을 원할 경우 아래 주석 해제
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        # 메뉴바를 초기에 보이지 않도록 숨김 (높이 0으로 설정)
        self.menuBar().setFixedHeight(0)
        self.menu_visible = False  # 메뉴바 표시 여부를 추적하는 플래그

        # 메뉴바에 대한 애니메이션 설정
        self.menu_anim = QPropertyAnimation(self.menuBar(), b"maximumHeight")
        self.menu_anim.setDuration(200)  # 메뉴 애니메이션 지속 시간 (밀리초 단위)

        # 마우스 위치를 주기적으로 체크하기 위한 타이머 설정
        self.mouse_timer = QTimer(self)
        self.mouse_timer.setInterval(100)  # 0.1초마다 위치 확인
        self.mouse_timer.timeout.connect(self.check_mouse_position)  # 타이머와 메서드 연결
        self.mouse_timer.start()

        # plainTextEdit 위젯의 객체 이름을 간단히 참조
        editor = self.plain_te

        # 파일 메뉴의 각 액션을 기능에 연결
        self.actionOpen.triggered.connect(self.open_file)        # 열기
        self.actionSave.triggered.connect(self.save_file)        # 저장
        self.actionSave_as.triggered.connect(self.save_file_as)  # 다른 이름으로 저장
        self.actionExit.triggered.connect(self.close)            # 종료
        self.actionNew.triggered.connect(self.new_file)          # 새 문서

        # 편집 메뉴 기능 연결
        self.actionUndo.triggered.connect(editor.undo)           # 실행 취소
        self.actionRedo.triggered.connect(editor.redo)           # 다시 실행
        self.actionCut.triggered.connect(editor.cut)             # 잘라내기
        self.actionCopy.triggered.connect(editor.copy)           # 복사
        self.actionPaste.triggered.connect(editor.paste)         # 붙여넣기
        self.actionSelect_All.triggered.connect(editor.selectAll) # 전체 선택
        self.actionFont.triggered.connect(self.change_font)      # 글꼴 변경
        self.actionDelete.triggered.connect(self.delete_text)    # 텍스트 삭제

        # 도움말 메뉴 연결
        self.actionAbout.triggered.connect(self.show_about)      # 정보창

        # 현재 열려 있는 파일 경로 저장 변수
        self.current_file = None

        # 창 제목을 현재 상태에 맞게 업데이트
        self.update_window_title()

    # 파일 열기 기능 구현
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

    # 파일 저장 기능
    def save_file(self):
        if self.current_file:  # 기존에 열려 있는 파일이 있을 경우
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.plain_te.toPlainText())  # 현재 텍스트 저장
            self.plain_te.document().setModified(False)
        else:  # 새 문서인 경우
            self.save_file_as()

    # '다른 이름으로 저장' 기능
    def save_file_as(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(self.plain_te.toPlainText())  # 내용 저장
            self.current_file = fname
            self.plain_te.document().setModified(False)
            self.update_window_title()  # 제목 업데이트

    # 글꼴 변경 대화상자
    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.plain_te.setFont(font)  # 사용자가 선택한 글꼴 적용

    # 프로그램 정보창 표시
    def show_about(self):
        QMessageBox.information(self, "About", "Qt Notepad\nMade with PyQt5")
        #QMessageBox.about(self, 'Qt Note Pad',
        #                  '만든이 : ABC Lab\n\r버전 정보 : 1.0.0.0')

    # 텍스트 삭제 기능
    def delete_text(self):
        if not self.plain_te:
            return

        cursor = self.plain_te.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()  # 선택된 텍스트 삭제
        else:
            cursor.deleteChar()  # 선택이 없으면 커서 위치 문자 삭제
        self.plain_te.setTextCursor(cursor)  # 커서 상태 업데이트

    # 새 파일 생성 (기존 내용 저장 여부 확인 포함)
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

        # ✅ 여기부터는 진짜 저장 완료됐을 때만 실행
        self.plain_te.clear()
        self.current_file = None
        self.update_window_title()

    # 윈도우 타이틀을 현재 파일 이름으로 설정
    def update_window_title(self):
        if self.current_file:
            filename = self.current_file.split("/")[-1]  # 경로를 제외한 파일 이름 추출
        else:
            filename = "제목없음"

        self.setWindowTitle(f"{filename} - Qt Note Pad")

    # 마우스 위치 감지하여 메뉴바 보이거나 숨기기
    def check_mouse_position(self):
        pos = self.mapFromGlobal(QCursor.pos())  # 현재 마우스 위치를 윈도우 기준으로 변환
        if pos.y() <= 10:
            self.show_menu_bar()  # 화면 상단에 마우스 접근 시 메뉴바 표시
        elif pos.y() > 50:
            self.hide_menu_bar()  # 화면을 벗어나면 메뉴바 숨김

    # 메뉴바 보이기 애니메이션 실행
    def show_menu_bar(self):
        if not self.menu_visible:
            self.menu_visible = True
            self.menu_anim.stop()
            self.menu_anim.setStartValue(0)
            self.menu_anim.setEndValue(30)  # 보일 때 높이 설정
            self.menu_anim.start()

    # 메뉴바 숨기기 애니메이션 실행
    def hide_menu_bar(self):
        if self.menu_visible:
            self.menu_visible = False
            self.menu_anim.stop()
            self.menu_anim.setStartValue(30)
            self.menu_anim.setEndValue(0)  # 숨길 때 높이 설정
            self.menu_anim.start()

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

# 프로그램의 진입점. 실제로 GUI 실행
if __name__ == "__main__":
    app = QApplication(sys.argv)    # 앱 객체 생성
    main_window = ExampleApp()      # 메인 윈도우 객체 생성
    main_window.show()              # 메인 윈도우 표시
    sys.exit(app.exec_())           # 이벤트 루프 진입 (종료 시 시스템 종료)
