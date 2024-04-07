![](image_files/bg_img.jpg)

# Calorie for Diet
바코드 및 음식물 사진을 통하여 칼로리를 자동으로 계산해줍니다.
설정한 칼로리의 초과 또는 미만 여부를 표시해주며 한 눈에 영양 정보를 볼 수 있습니다.
<br><br/>

# 시연 영상
[👉클릭](https://www.youtube.com/watch?v=CDB5UjjE3v4)
<br><br/>

# 팀 소개
: 서예선 - Frontend

: 이지수 - Backend

: 이채은 - Frontend

: 최정은 - Backend
<br><br/>


# 사용 방법
0. `git clone https://github.com/jungeun919/Calorie-for-Diet.git` <!-- → 해당 저장소로부터 프로젝트 복제 -->

1. yolov3.weights 파일을 다운 받아 폴더에 넣기

2. `. venv/scripts/activate` → 가상환경 실행

3. `flask db migrate` → 마이그레이션 실행

4. `flask db upgrade` → 테이블 생성

5. `export FLASK_APP=__init__` → 환경변수 설정

6. `pip install -r requirements.txt` → requirements.txt 파일 안에 있는 패키지 모두 설치

7. `flask run` → 서버 실행
<br>