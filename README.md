# 📝 Qt Note Pad

PyQt5 기반 노트패드 + 뮤직플레이어 + YouTube 다운로더

## 🚀 설치 및 실행

### 1. 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 2. 실행
```bash
python note_mp3player.py
```

## ✨ 기능

### 📋 노트패드
- 텍스트 파일 열기/저장
- 복사/붙여넣기, 실행취소
- 글꼴 변경, 커스텀 테마
- 프레임리스 윈도우

### 🎵 뮤직플레이어 (Widgets 메뉴에서 추가)
- 폴더 단위 음악 재생
- MP3, WAV, OGG, FLAC 지원
- 셔플, 반복 재생
- 볼륨 조절, 진행률 표시

### 📥 YouTube 다운로더 (Widgets 메뉴에서 추가)
- YouTube 검색 및 다운로드
- 자동 FFmpeg 설치 (MP3 변환)
- 고품질/최고품질 선택

## 📁 파일 구조
```
├── note_mp3player.py          # 메인 프로그램
├── QtNotepad.ui              # UI 파일
├── widgets/                  # 위젯 폴더
│   ├── musicPlayer.py
│   └── youtubeDownloader.py
└── requirements.txt
```

## 🔧 사용법

1. **프로그램 실행**
   ```bash
   python note_mp3player.py
   ```

2. **위젯 추가**
   - 메뉴바 → Widgets → 원하는 위젯 선택

3. **뮤직플레이어**
   - 음악 폴더 열기 → 재생목록에서 곡 선택

4. **YouTube 다운로더**
   - FFmpeg 자동 설치 (첫 사용시)
   - 검색 또는 URL 입력 → 다운로드

## 🛠️ 문제 해결

### 파일 메뉴 오류
UI 파일 경로 확인:
```python
# note_mp3player.py에서
form_class = uic.loadUiType("./QtNotepad.ui")[0]
```

### PyQt5 설치 실패
```bash
pip install --upgrade pip
pip install PyQt5 --force-reinstall
```

### 음악 재생 안됨
- 지원 형식: MP3, WAV, OGG, M4A, FLAC
- 파일 경로에 한글 확인

### YouTube 다운로드 실패
```bash
pip install --upgrade yt-dlp
```

## 📋 필수 라이브러리
- PyQt5 (GUI)
- mutagen (음악 메타데이터)
- yt-dlp (YouTube 다운로드)
- requests (HTTP 요청)

## 🎯 새 위젯 추가

`widgets/` 폴더에 `.py` 파일 생성:

```python
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("내 위젯"))

def create_widget():
    return MyWidget()
```

---
**파일 메뉴 오류가 발생하면 QtNotepad.ui 파일이 같은 폴더에 있는지 확인하세요.**
