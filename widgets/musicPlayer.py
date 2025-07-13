# musicPlayer.py
import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import random


class MusicPlayerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_media_player()
        self.current_folder = None
        self.playlist_files = []
        self.current_index = 0
        self.is_shuffled = False
        self.repeat_mode = 0  # 0: 반복없음, 1: 전체반복, 2: 한곡반복

    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 상단: 폴더 선택 버튼
        folder_layout = QHBoxLayout()
        self.folder_btn = QPushButton("🎵 음악 폴더 열기")
        self.folder_btn.setMinimumHeight(35)
        self.folder_btn.clicked.connect(self.open_music_folder)
        folder_layout.addWidget(self.folder_btn)
        main_layout.addLayout(folder_layout)

        # 현재 재생 정보 표시
        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.StyledPanel)
        self.info_frame.setMinimumHeight(80)
        info_layout = QVBoxLayout(self.info_frame)

        self.title_label = QLabel("재생할 음악을 선택해주세요")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignCenter)
        self.artist_label.setStyleSheet("color: #666; font-size: 12px;")

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)
        main_layout.addWidget(self.info_frame)

        # 진행률 표시 및 컨트롤
        progress_layout = QVBoxLayout()

        # 시간 정보
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setStyleSheet("font-size: 11px;")
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setStyleSheet("font-size: 11px;")

        # 진행률 슬라이더
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        self.slider_dragging = False

        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(self.progress_slider)
        time_layout.addWidget(self.total_time_label)

        progress_layout.addLayout(time_layout)
        main_layout.addLayout(progress_layout)

        # 재생 컨트롤 버튼들
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)

        # 셔플 버튼
        self.shuffle_btn = QPushButton("🔀")
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.shuffle_btn.setToolTip("셔플")

        # 이전곡 버튼
        self.prev_btn = QPushButton("⏮️")
        self.prev_btn.clicked.connect(self.previous_track)
        self.prev_btn.setToolTip("이전곡")

        # 재생/일시정지 버튼
        self.play_btn = QPushButton("▶️")
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setToolTip("재생/일시정지")
        self.play_btn.setMinimumSize(50, 40)

        # 다음곡 버튼
        self.next_btn = QPushButton("⏭️")
        self.next_btn.clicked.connect(self.next_track)
        self.next_btn.setToolTip("다음곡")

        # 반복 버튼
        self.repeat_btn = QPushButton("🔁")
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        self.repeat_btn.setToolTip("반복모드")

        for btn in [self.shuffle_btn, self.prev_btn, self.play_btn,
                    self.next_btn, self.repeat_btn]:
            btn.setMinimumSize(35, 35)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ccc;
                    border-radius: 17px;
                    background-color: #f0f0f0;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
                QPushButton:checked {
                    background-color: #007ACC;
                    color: white;
                }
            """)

        control_layout.addStretch()
        control_layout.addWidget(self.shuffle_btn)
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.next_btn)
        control_layout.addWidget(self.repeat_btn)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        # 볼륨 컨트롤
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        main_layout.addLayout(volume_layout)

        # 재생목록
        playlist_label = QLabel("📋 재생목록")
        playlist_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(playlist_label)

        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_track)
        self.playlist_widget.setAlternatingRowColors(True)
        main_layout.addWidget(self.playlist_widget)

        # 현재 재생중인 항목 스타일
        self.current_item_style = """
            QListWidget::item:selected {
                background-color: #007ACC;
                color: white;
            }
        """
        self.playlist_widget.setStyleSheet(self.current_item_style)

    def init_media_player(self):
        self.media_player = QMediaPlayer()
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.mediaStatusChanged.connect(self.media_status_changed)

        # 볼륨 초기 설정
        self.media_player.setVolume(70)

    def open_music_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "음악 폴더 선택")
        if folder:
            self.current_folder = folder
            self.load_music_files(folder)

    def load_music_files(self, folder):
        """음악 파일들을 로드하고 재생목록을 업데이트"""
        self.playlist_files.clear()
        self.playlist_widget.clear()

        # 지원하는 오디오 형식
        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']

        try:
            for file in os.listdir(folder):
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    file_path = os.path.join(folder, file)
                    self.playlist_files.append(file_path)

                    # 메타데이터 추출
                    display_name = self.get_track_display_name(file_path)

                    item = QListWidgetItem(display_name)
                    item.setData(Qt.UserRole, file_path)
                    self.playlist_widget.addItem(item)

            if self.playlist_files:
                self.folder_btn.setText(f"🎵 로드됨: {len(self.playlist_files)}곡")
                self.current_index = 0
            else:
                QMessageBox.information(self, "알림", "선택한 폴더에 음악 파일이 없습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"폴더 로드 중 오류가 발생했습니다: {str(e)}")

    def get_track_display_name(self, file_path):
        """파일의 메타데이터에서 제목과 아티스트 정보를 추출"""
        try:
            if file_path.lower().endswith('.mp3'):
                audio_file = MP3(file_path, ID3=ID3)
                title = str(audio_file.get('TIT2', '')) if audio_file.get('TIT2') else None
                artist = str(audio_file.get('TPE1', '')) if audio_file.get('TPE1') else None

                if title and artist:
                    return f"{artist} - {title}"
                elif title:
                    return title

        except Exception:
            pass

        # 메타데이터를 읽을 수 없으면 파일명 사용
        return os.path.splitext(os.path.basename(file_path))[0]

    def play_selected_track(self, item):
        """재생목록에서 선택된 트랙 재생"""
        file_path = item.data(Qt.UserRole)
        if file_path in self.playlist_files:
            self.current_index = self.playlist_files.index(file_path)
            self.play_current_track()

    def play_current_track(self):
        """현재 인덱스의 트랙 재생"""
        if not self.playlist_files or self.current_index >= len(self.playlist_files):
            return

        file_path = self.playlist_files[self.current_index]
        media_content = QMediaContent(QUrl.fromLocalFile(file_path))
        self.media_player.setMedia(media_content)

        # 현재 재생 정보 업데이트
        self.update_current_track_info(file_path)

        # 재생목록에서 현재 항목 강조
        self.highlight_current_track()

        self.media_player.play()

    def update_current_track_info(self, file_path):
        """현재 재생 중인 트랙 정보 업데이트"""
        try:
            if file_path.lower().endswith('.mp3'):
                audio_file = MP3(file_path, ID3=ID3)
                title = str(audio_file.get('TIT2', '')) if audio_file.get('TIT2') else \
                os.path.splitext(os.path.basename(file_path))[0]
                artist = str(audio_file.get('TPE1', '')) if audio_file.get('TPE1') else "알 수 없는 아티스트"

                self.title_label.setText(title)
                self.artist_label.setText(artist)
            else:
                filename = os.path.splitext(os.path.basename(file_path))[0]
                self.title_label.setText(filename)
                self.artist_label.setText("알 수 없는 아티스트")

        except Exception:
            filename = os.path.splitext(os.path.basename(file_path))[0]
            self.title_label.setText(filename)
            self.artist_label.setText("알 수 없는 아티스트")

    def highlight_current_track(self):
        """재생목록에서 현재 재생 중인 트랙 강조"""
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            if i == self.current_index:
                item.setBackground(QColor("#007ACC"))
                item.setForeground(QColor("white"))
            else:
                item.setBackground(QColor())
                item.setForeground(QColor())

    def toggle_playback(self):
        """재생/일시정지 토글"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            if not self.playlist_files:
                QMessageBox.information(self, "알림", "먼저 음악 폴더를 선택해주세요.")
                return
            if self.media_player.state() == QMediaPlayer.StoppedState:
                self.play_current_track()
            else:
                self.media_player.play()

    def previous_track(self):
        """이전 곡으로 이동"""
        if not self.playlist_files:
            return

        if self.is_shuffled:
            # 셔플 모드에서는 랜덤하게 선택
            self.current_index = random.randint(0, len(self.playlist_files) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist_files)

        self.play_current_track()

    def next_track(self):
        """다음 곡으로 이동"""
        if not self.playlist_files:
            return

        if self.is_shuffled:
            # 셔플 모드에서는 랜덤하게 선택
            self.current_index = random.randint(0, len(self.playlist_files) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist_files)

        self.play_current_track()

    def toggle_shuffle(self):
        """셔플 모드 토글"""
        self.is_shuffled = self.shuffle_btn.isChecked()
        if self.is_shuffled:
            self.shuffle_btn.setToolTip("셔플 ON")
        else:
            self.shuffle_btn.setToolTip("셔플 OFF")

    def toggle_repeat(self):
        """반복 모드 토글 (없음 -> 전체반복 -> 한곡반복 -> 없음)"""
        self.repeat_mode = (self.repeat_mode + 1) % 3

        if self.repeat_mode == 0:
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setToolTip("반복 OFF")
            self.repeat_btn.setChecked(False)
        elif self.repeat_mode == 1:
            self.repeat_btn.setText("🔁")
            self.repeat_btn.setToolTip("전체반복")
            self.repeat_btn.setChecked(True)
        else:  # repeat_mode == 2
            self.repeat_btn.setText("🔂")
            self.repeat_btn.setToolTip("한곡반복")
            self.repeat_btn.setChecked(True)

    def change_volume(self, value):
        """볼륨 변경"""
        self.media_player.setVolume(value)

    def slider_pressed(self):
        """진행률 슬라이더가 눌렸을 때"""
        self.slider_dragging = True

    def slider_released(self):
        """진행률 슬라이더가 놓였을 때"""
        self.slider_dragging = False
        if self.media_player.duration() > 0:
            position = int(self.progress_slider.value() * self.media_player.duration() / 100)
            self.media_player.setPosition(position)

    def media_state_changed(self, state):
        """미디어 재생 상태가 변경되었을 때"""
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸️")
            self.play_btn.setToolTip("일시정지")
        else:
            self.play_btn.setText("▶️")
            self.play_btn.setToolTip("재생")

    def position_changed(self, position):
        """재생 위치가 변경되었을 때"""
        if not self.slider_dragging and self.media_player.duration() > 0:
            progress = int(position * 100 / self.media_player.duration())
            self.progress_slider.setValue(progress)

        # 현재 시간 표시 업데이트
        current_time = self.format_time(position)
        self.current_time_label.setText(current_time)

    def duration_changed(self, duration):
        """재생 시간이 변경되었을 때"""
        total_time = self.format_time(duration)
        self.total_time_label.setText(total_time)

    def media_status_changed(self, status):
        """미디어 상태가 변경되었을 때"""
        if status == QMediaPlayer.EndOfMedia:
            # 곡이 끝났을 때
            if self.repeat_mode == 2:  # 한곡반복
                self.play_current_track()
            elif self.repeat_mode == 1:  # 전체반복
                self.next_track()
            elif self.current_index < len(self.playlist_files) - 1:  # 마지막 곡이 아닌 경우
                self.next_track()
            else:  # 마지막 곡이고 반복 모드가 아닌 경우
                self.media_player.stop()

    def format_time(self, milliseconds):
        """밀리초를 mm:ss 형식으로 변환"""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


def create_widget():
    """위젯 생성 함수 (메인 앱에서 호출)"""
    return MusicPlayerWidget()