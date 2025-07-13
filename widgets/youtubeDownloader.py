# autoFFmpegDownloader.py - FFmpeg 자동 설치 및 MP3 변환
import os
import sys
import re
import zipfile
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    yt_dlp = None


class AutoFFmpegDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.init_attributes()
        self.init_ui()

    def init_attributes(self):
        """속성 초기화"""
        try:
            home_path = os.path.expanduser("~")
            self.default_download_path = os.path.join(home_path, "Downloads", "YouTube_MP3")
            os.makedirs(self.default_download_path, exist_ok=True)

            # FFmpeg 경로 설정 (프로그램 폴더 내)
            self.ffmpeg_dir = os.path.join(os.path.dirname(__file__), "ffmpeg")
            os.makedirs(self.ffmpeg_dir, exist_ok=True)

        except Exception:
            self.default_download_path = os.getcwd()
            self.ffmpeg_dir = os.getcwd()

        self.search_results_data = []
        self.ffmpeg_available = False

    def init_ui(self):
        """UI 구성"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 크기 제한
        self.setMaximumWidth(380)
        self.setMinimumWidth(350)

        # 제목
        title = QLabel("📥 YouTube MP3 다운로더")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # FFmpeg 상태 및 설치
        self.create_ffmpeg_section(main_layout)

        # 라이브러리 상태 체크
        if not YT_DLP_AVAILABLE:
            self.show_library_warning(main_layout)

        # 검색 영역
        self.create_search_section(main_layout)

        # URL 입력 영역
        self.create_url_section(main_layout)

        # 설정 영역
        self.create_settings_section(main_layout)

        # 저장 폴더
        self.create_folder_section(main_layout)

        # 상태 및 다운로드
        self.create_download_section(main_layout)

        # 초기 FFmpeg 체크
        self.check_and_update_ffmpeg_status()

    def create_ffmpeg_section(self, layout):
        """FFmpeg 섹션 생성"""
        ffmpeg_frame = QFrame()
        ffmpeg_frame.setFrameStyle(QFrame.StyledPanel)
        ffmpeg_layout = QVBoxLayout(ffmpeg_frame)
        ffmpeg_layout.setContentsMargins(8, 8, 8, 8)

        # 상태 표시
        self.ffmpeg_status_label = QLabel("FFmpeg 상태 확인 중...")
        self.ffmpeg_status_label.setAlignment(Qt.AlignCenter)
        self.ffmpeg_status_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        ffmpeg_layout.addWidget(self.ffmpeg_status_label)

        # 설치 버튼
        self.install_ffmpeg_btn = QPushButton("🔧 FFmpeg 자동 설치 (MP3 변환용)")
        self.install_ffmpeg_btn.clicked.connect(self.install_ffmpeg)
        self.install_ffmpeg_btn.setVisible(False)
        self.install_ffmpeg_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        ffmpeg_layout.addWidget(self.install_ffmpeg_btn)

        layout.addWidget(ffmpeg_frame)

    def check_and_update_ffmpeg_status(self):
        """FFmpeg 상태 확인 및 업데이트"""
        self.ffmpeg_available = self.check_ffmpeg()

        if self.ffmpeg_available:
            self.ffmpeg_status_label.setText("✅ FFmpeg 사용 가능 - MP3 변환 지원")
            self.ffmpeg_status_label.setStyleSheet("color: green; font-weight: bold; font-size: 11px;")
            self.install_ffmpeg_btn.setVisible(False)
        else:
            self.ffmpeg_status_label.setText("⚠️ FFmpeg 없음 - MP3 변환 불가")
            self.ffmpeg_status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 11px;")
            self.install_ffmpeg_btn.setVisible(True)

    def check_ffmpeg(self):
        """FFmpeg 사용 가능 여부 확인"""
        try:
            import subprocess

            # 시스템 PATH에서 확인
            try:
                subprocess.run(['ffmpeg', '-version'],
                               capture_output=True, check=True, timeout=3)
                return True
            except:
                pass

            # 로컬 ffmpeg 폴더에서 확인
            ffmpeg_exe = os.path.join(self.ffmpeg_dir, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                try:
                    subprocess.run([ffmpeg_exe, '-version'],
                                   capture_output=True, check=True, timeout=3)
                    return True
                except:
                    pass

            return False

        except Exception:
            return False

    def install_ffmpeg(self):
        """FFmpeg 자동 설치"""
        reply = QMessageBox.question(
            self,
            "FFmpeg 설치",
            "FFmpeg를 자동으로 다운로드하고 설치하시겠습니까?\n"
            "MP3 변환을 위해 필요합니다.\n\n"
            "크기: 약 50MB, 시간: 1-2분",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self.install_ffmpeg_btn.setEnabled(False)
            self.install_ffmpeg_btn.setText("다운로드 중...")
            self.ffmpeg_status_label.setText("FFmpeg 다운로드 중... 잠시만 기다려주세요")

            # 별도 스레드에서 다운로드 (간단하게 타이머 사용)
            QTimer.singleShot(500, self.download_ffmpeg)

    def download_ffmpeg(self):
        """FFmpeg 다운로드 및 설치"""
        try:
            # Windows용 FFmpeg 다운로드 URL (GitHub releases)
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

            self.ffmpeg_status_label.setText("다운로드 중... (50MB)")

            # 다운로드
            response = requests.get(ffmpeg_url, stream=True, timeout=30)
            response.raise_for_status()

            zip_path = os.path.join(self.ffmpeg_dir, "ffmpeg.zip")

            # 파일 저장
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.ffmpeg_status_label.setText(f"다운로드 중... {progress}%")

            self.ffmpeg_status_label.setText("압축 해제 중...")

            # 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # ffmpeg.exe와 ffprobe.exe만 추출
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith(('ffmpeg.exe', 'ffprobe.exe')):
                        file_info.filename = os.path.basename(file_info.filename)
                        zip_ref.extract(file_info, self.ffmpeg_dir)

            # 임시 파일 삭제
            os.remove(zip_path)

            # 설치 확인
            if self.check_ffmpeg():
                self.ffmpeg_status_label.setText("✅ FFmpeg 설치 완료!")
                self.ffmpeg_status_label.setStyleSheet("color: green; font-weight: bold; font-size: 11px;")
                self.install_ffmpeg_btn.setVisible(False)
                self.ffmpeg_available = True
                QMessageBox.information(self, "완료", "FFmpeg 설치가 완료되었습니다!\n이제 MP3 변환이 가능합니다.")
            else:
                raise Exception("설치 후 FFmpeg 실행 실패")

        except Exception as e:
            self.ffmpeg_status_label.setText("❌ 설치 실패")
            self.ffmpeg_status_label.setStyleSheet("color: red; font-weight: bold; font-size: 11px;")
            self.install_ffmpeg_btn.setText("🔧 FFmpeg 자동 설치 (MP3 변환용)")
            self.install_ffmpeg_btn.setEnabled(True)
            QMessageBox.critical(self, "설치 실패", f"FFmpeg 설치 중 오류가 발생했습니다:\n{str(e)}")

    def show_library_warning(self, layout):
        """yt-dlp 라이브러리 경고"""
        warning_frame = QFrame()
        warning_frame.setFrameStyle(QFrame.StyledPanel)
        warning_frame.setStyleSheet("background-color: #f8d7da; border: 1px solid #f5c6cb;")
        warning_layout = QVBoxLayout(warning_frame)

        warning = QLabel("❌ yt-dlp 라이브러리가 필요합니다")
        warning.setStyleSheet("color: #721c24; font-weight: bold;")
        warning.setAlignment(Qt.AlignCenter)

        install_cmd = QLabel("설치: pip install yt-dlp")
        install_cmd.setStyleSheet("color: #721c24; font-family: monospace; font-size: 11px;")
        install_cmd.setAlignment(Qt.AlignCenter)

        warning_layout.addWidget(warning)
        warning_layout.addWidget(install_cmd)
        layout.addWidget(warning_frame)

    def create_search_section(self, layout):
        """검색 섹션"""
        search_group = QFrame()
        search_group.setFrameStyle(QFrame.StyledPanel)
        search_layout = QVBoxLayout(search_group)
        search_layout.setContentsMargins(8, 8, 8, 8)

        search_label = QLabel("🔍 유튜브 검색")
        search_label.setStyleSheet("font-weight: bold; color: #333;")
        search_layout.addWidget(search_label)

        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요...")
        self.search_input.returnPressed.connect(self.search_youtube)

        self.search_btn = QPushButton("검색")
        self.search_btn.setMaximumWidth(60)
        self.search_btn.clicked.connect(self.search_youtube)
        self.search_btn.setEnabled(YT_DLP_AVAILABLE)

        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_btn)
        search_layout.addLayout(search_input_layout)

        self.results_combo = QComboBox()
        self.results_combo.setVisible(False)
        self.results_combo.currentTextChanged.connect(self.on_result_selected)
        search_layout.addWidget(self.results_combo)

        layout.addWidget(search_group)

    def create_url_section(self, layout):
        """URL 입력 섹션"""
        url_group = QFrame()
        url_group.setFrameStyle(QFrame.StyledPanel)
        url_layout = QVBoxLayout(url_group)
        url_layout.setContentsMargins(8, 8, 8, 8)

        url_label = QLabel("🔗 또는 직접 URL 입력")
        url_label.setStyleSheet("font-weight: bold; color: #333;")
        url_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(self.url_input)

        layout.addWidget(url_group)

    def create_settings_section(self, layout):
        """설정 섹션"""
        settings_layout = QHBoxLayout()

        quality_label = QLabel("품질:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["고품질 MP3", "최고품질 MP3", "원본 오디오"])
        self.quality_combo.setMaximumWidth(120)

        settings_layout.addWidget(quality_label)
        settings_layout.addWidget(self.quality_combo)
        settings_layout.addStretch()
        layout.addLayout(settings_layout)

    def create_folder_section(self, layout):
        """폴더 선택 섹션"""
        folder_layout = QVBoxLayout()
        folder_label = QLabel("💾 저장 폴더")
        folder_label.setStyleSheet("font-weight: bold; color: #333;")
        folder_layout.addWidget(folder_label)

        folder_select_layout = QHBoxLayout()
        self.folder_display = QLineEdit()
        self.folder_display.setText(self.default_download_path)
        self.folder_display.setReadOnly(True)
        self.folder_display.setStyleSheet("background-color: #f5f5f5;")

        self.browse_btn = QPushButton("찾아보기")
        self.browse_btn.setMaximumWidth(80)
        self.browse_btn.clicked.connect(self.browse_folder)

        folder_select_layout.addWidget(self.folder_display)
        folder_select_layout.addWidget(self.browse_btn)
        folder_layout.addLayout(folder_select_layout)
        layout.addLayout(folder_layout)

    def create_download_section(self, layout):
        """다운로드 섹션"""
        self.status_label = QLabel("대기 중...")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        layout.addWidget(self.progress_bar)

        self.download_btn = QPushButton("⬇️ MP3 다운로드")
        self.download_btn.setMinimumHeight(40)
        self.download_btn.clicked.connect(self.download_mp3)
        self.download_btn.setEnabled(YT_DLP_AVAILABLE)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #ccc; color: #666; }
        """)
        layout.addWidget(self.download_btn)

    def search_youtube(self):
        """유튜브 검색"""
        if not YT_DLP_AVAILABLE:
            QMessageBox.warning(self, "경고", "yt-dlp 라이브러리가 필요합니다.\npip install yt-dlp")
            return

        query = self.search_input.text().strip()
        if not query:
            return

        self.search_btn.setEnabled(False)
        self.search_btn.setText("검색중...")

        QTimer.singleShot(100, lambda: self.perform_search(query))

    def perform_search(self, query):
        """검색 수행"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch3:{query}", download=False)

                self.search_results_data.clear()
                self.results_combo.clear()

                if info and 'entries' in info:
                    self.results_combo.addItem("-- 검색 결과 선택 --")

                    for entry in info['entries']:
                        if entry and entry.get('id'):
                            title = str(entry.get('title', '제목 없음'))
                            url = f"https://www.youtube.com/watch?v={entry.get('id')}"

                            display_title = title[:40] + "..." if len(title) > 40 else title
                            self.results_combo.addItem(display_title)
                            self.search_results_data.append({'title': title, 'url': url})

                    self.results_combo.setVisible(True)
                    self.status_label.setText(f"검색 완료: {len(self.search_results_data)}개")

        except Exception as e:
            self.status_label.setText("검색 실패")
            QMessageBox.warning(self, "오류", "검색 중 오류가 발생했습니다.")

        finally:
            self.search_btn.setEnabled(True)
            self.search_btn.setText("검색")

    def on_result_selected(self, text):
        """검색 결과 선택"""
        if text and text != "-- 검색 결과 선택 --":
            index = self.results_combo.currentIndex() - 1
            if 0 <= index < len(self.search_results_data):
                self.url_input.setText(self.search_results_data[index]['url'])

    def browse_folder(self):
        """폴더 선택"""
        folder = QFileDialog.getExistingDirectory(self, "저장 폴더", self.folder_display.text())
        if folder:
            self.folder_display.setText(folder)

    def download_mp3(self):
        """MP3 다운로드"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력하세요.")
            return

        if not YT_DLP_AVAILABLE:
            QMessageBox.warning(self, "경고", "yt-dlp 라이브러리가 필요합니다.")
            return

        self.download_btn.setEnabled(False)
        self.download_btn.setText("다운로드 중...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        QTimer.singleShot(100, lambda: self.perform_download(url))

    def perform_download(self, url):
        """실제 다운로드 수행"""
        try:
            output_path = self.folder_display.text()
            quality = self.quality_combo.currentText()

            if self.ffmpeg_available:
                # FFmpeg 사용 가능 - MP3 변환
                if "원본" in quality:
                    ydl_opts = {
                        'format': 'bestaudio',
                        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                        'quiet': True,
                    }
                else:
                    quality_map = {
                        "고품질 MP3": "192",
                        "최고품질 MP3": "320"
                    }

                    # 로컬 FFmpeg 경로 지정
                    ffmpeg_path = os.path.join(self.ffmpeg_dir, "ffmpeg.exe")
                    if os.path.exists(ffmpeg_path):
                        ffmpeg_location = ffmpeg_path
                    else:
                        ffmpeg_location = None

                    ydl_opts = {
                        'format': 'bestaudio',
                        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': quality_map.get(quality, "192"),
                        }],
                        'quiet': True,
                    }

                    if ffmpeg_location:
                        ydl_opts['ffmpeg_location'] = ffmpeg_location
            else:
                # FFmpeg 없음 - 원본 다운로드
                ydl_opts = {
                    'format': 'bestaudio',
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'quiet': True,
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.setText("✅ 다운로드 완료!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            QMessageBox.information(self, "완료", "다운로드가 완료되었습니다!")

        except Exception as e:
            self.status_label.setText("❌ 다운로드 실패")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "오류", f"다운로드 실패:\n{str(e)}")

        finally:
            self.download_btn.setEnabled(True)
            self.download_btn.setText("⬇️ MP3 다운로드")
            self.progress_bar.setVisible(False)
            QTimer.singleShot(3000, lambda: self.status_label.setStyleSheet("color: #666; font-size: 12px;"))


def create_widget():
    """위젯 생성 함수"""
    return AutoFFmpegDownloader()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AutoFFmpegDownloader()
    widget.show()
    sys.exit(app.exec_())