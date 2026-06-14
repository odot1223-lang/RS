# RS

RoboCupJunior Rescue Simulation 2026 controller project.

이 저장소는 Webots/Erebus 기반 RoboCupJunior Rescue Simulation을 위한 Python 구조 로봇 컨트롤러입니다. 로봇이 미로를 자율 탐색하고, 벽/바닥/특수 타일을 매핑하며, 피해자 표식과 cognitive target을 인식해 서버에 보고하도록 구성되어 있습니다.

## 주요 기능

- 라이다 기반 벽/장애물 매핑
- 카메라 기반 바닥 타일 인식
  - hole
  - swamp
  - checkpoint
- 2026 규정 표식 인식
  - letter victims: `H`, `S`, `U`
  - cognitive targets: `F`, `P`, `C`, `O`
- A* 기반 경로 탐색
- 미탐색 구역 자동 탐색
- 피해자/표식 보고
- 최종 맵 생성 및 전송
- 초보자용 고수준 API `RescueRobot`
- OpenCV 실시간 맵 시각화

## 프로젝트 구조

```text
.
├── robot_jsons/
│   └── robot5.json
├── src/
│   ├── main.py                         # 실행 예시 선택 파일
│   ├── run.py                          # Erebus/Webots 실행 진입점
│   ├── rescue_robot.py                 # 초보자용 고수준 API
│   ├── flags.py                        # 디버그/시각화 플래그
│   ├── executor/                       # 상태 머신, 미션 실행 흐름
│   ├── robot/                          # Webots 장치 래퍼 및 이동 제어
│   ├── mapping/                        # 벽, 바닥, 점유 영역 매핑
│   ├── fixture_detection/              # 피해자 및 cognitive target 인식
│   ├── agent/                          # 목표 선택 및 경로 탐색 에이전트
│   ├── final_matrix_creation/          # 최종 제출 맵 생성
│   ├── flow_control/                   # 지연, 시퀀스, 상태 머신 유틸
│   └── data_structures/                # 좌표, 각도, 그리드 자료구조
```

## 실행 방법

1. RoboCupJunior Rescue Simulation/Erebus 환경을 준비합니다.
2. 이 저장소의 `src` 폴더가 컨트롤러 코드로 복사되거나 참조되도록 설정합니다.
3. Webots/Erebus에서 컨트롤러 진입점을 `src/run.py`로 실행합니다.
4. 기본 실행은 [src/main.py](src/main.py)의 마지막 줄에서 선택합니다.

기본값은 완전 자율 주행입니다.

```python
example_autonomous()
```

다른 실행 방식을 쓰고 싶으면 [src/main.py](src/main.py) 하단에서 원하는 예시만 주석 해제하세요.

```python
# example_autonomous()
example_manual_control()
```

## 빠른 사용 예시

```python
from rescue_robot import RescueRobot

robot = RescueRobot()
robot.run_autonomous()
```

직접 루프를 제어하려면:

```python
from rescue_robot import RescueRobot

robot = RescueRobot()

while robot.is_running():
    if robot.victim_visible and not robot.already_reported:
        robot.stop()
        robot.report_victim()
    else:
        robot.go_to_next_target()
```

## RescueRobot API

자주 쓰는 속성:

| 이름 | 설명 |
| --- | --- |
| `robot.x`, `robot.y` | 현재 위치 |
| `robot.location` | `(x, y)` 튜플 |
| `robot.direction` | 현재 방향, 도 단위 |
| `robot.elapsed_time` | 경과 시간 |
| `robot.remaining_time` | 남은 시간 |
| `robot.victim_visible` | 카메라에 보고 가능한 표식이 보이는지 |
| `robot.victim_letter` | 인식된 코드: `H/S/U/F/P/C/O` |
| `robot.already_reported` | 현재 위치에서 이미 보고했는지 |
| `robot.exploration_complete` | 탐색 완료 여부 |

자주 쓰는 메서드:

| 이름 | 설명 |
| --- | --- |
| `run_autonomous()` | 초기화부터 탐색, 보고, 맵 전송까지 자동 수행 |
| `is_running()` | Webots 한 프레임 진행 및 센서 업데이트 |
| `step()` | 자율 주행 상태 머신 한 프레임 실행 |
| `go_to_next_target()` | 에이전트가 선택한 다음 목표로 이동 |
| `go_to(x, y)` | 지정 좌표로 이동 |
| `go_to_start()` | 시작 위치로 복귀 |
| `report_victim()` | 현재 보이는 표식 보고 |
| `send_final_map()` | 최종 맵 전송 |
| `finish_mission()` | 맵 전송 후 종료 신호 전송 |

## 인식 규칙

2026 규정 기준으로 다음 코드를 보고합니다.

### Letter victims

| 코드 | 의미 |
| --- | --- |
| `H` | Harmed victim |
| `S` | Stable victim |
| `U` | Unharmed victim |

### Cognitive targets

Cognitive target은 5개 동심 원/링의 색상값을 중심에서 바깥쪽까지 합산해 분류합니다.

| 색상 | 값 |
| --- | ---: |
| Black | -2 |
| Red | -1 |
| Yellow | 0 |
| Green | 1 |
| Blue | 2 |

| 합계 | 보고 코드 |
| ---: | --- |
| 0 | `F` |
| 1 | `P` |
| 2 | `C` |
| 3 | `O` |

## 디버그 설정

[src/flags.py](src/flags.py)에서 디버그 기능을 켜고 끌 수 있습니다.

```python
SHOW_LIVE_MAP = 1
SHOW_FIXTURE_DEBUG = 0
SHOW_DEBUG = 0
```

대표 플래그:

| 플래그 | 설명 |
| --- | --- |
| `SHOW_LIVE_MAP` | OpenCV 실시간 맵 창 표시 |
| `SHOW_FIXTURE_DEBUG` | 표식 인식 중간 이미지 표시 |
| `SHOW_DEBUG` | 일반 디버그 로그 출력 |
| `DO_SLOW_DOWN` | 루프를 느리게 실행 |
| `TUNE_FILTER` | HSV 필터 튜닝 UI 활성화 |

## 주요 모듈 설명

- `robot/robot.py`: Webots 장치 초기화 및 센서/모터 통합
- `robot/drive_base.py`: 바퀴 제어, 회전, 좌표 이동
- `robot/pose_manager.py`: GPS/자이로 기반 위치 및 방향 관리
- `mapping/mapper.py`: 라이다, 카메라, 바닥 정보를 통합해 지도 갱신
- `mapping/wall_mapper.py`: 라이다 포인트 클라우드로 벽 확정
- `mapping/floor_mapper.py`: 카메라 이미지로 바닥 색상 매핑
- `fixture_detection/fixture_clasification.py`: 표식 후보 분류
- `fixture_detection/victim_clasification.py`: `H/S/U` 글자 분류
- `agent/agent.py`: 탐색 단계 및 목표 선택
- `executor/executor.py`: 전체 미션 상태 머신

## 필요 패키지

실행 환경에는 Webots/Erebus의 `controller` 모듈이 필요합니다.

Python 패키지:

```text
numpy
opencv-python
```

일반 로컬 Python 환경에서는 Webots의 `controller` 모듈이 없어 실행되지 않을 수 있습니다. 실제 실행은 Webots/Erebus 컨트롤러 환경에서 하는 것을 기준으로 합니다.

## 참고

- 이 프로젝트는 RoboCupJunior Rescue Simulation 2026 규정에 맞춰 작성되었습니다.
- 맵과 인식 성능은 시뮬레이터 버전, 카메라 색감, 조명, 맵 구성에 따라 HSV 필터 조정이 필요할 수 있습니다.
