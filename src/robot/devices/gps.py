import math

from data_structures.vectors import Position2D

from robot.devices.sensor import Sensor

class Gps(Sensor):
    """
    Webots GPS 센서를 이용해 로봇의 전역 위치(x, z → x, y)를 추적하는 클래스입니다.

    또한 두 타임스텝 사이의 위치 차이를 이용해 로봇이 직진할 때의 진행 방향(각도)을
    계산할 수 있습니다. 단, 직진 중일 때만 신뢰도가 높습니다.
    """
    def __init__(self, webots_device, time_step, coords_multiplier=1):
        super().__init__(webots_device, time_step)
        self.multiplier = coords_multiplier   # 좌표 스케일링 인수 (기본값 1)
        self.position = Position2D(0, 0)
        self.position_filter_alpha = 0.5
        self.__orientation_reference = self.position
        self.has_valid_position = False
        # Erebus 26 GPS includes millimeter-scale noise. Use a longer straight
        # baseline so that jitter is not interpreted as robot heading.
        self.orientation_min_displacement = 0.05

    def update(self):
        """매 타임스텝 호출: GPS 값을 갱신합니다."""
        measurement = self.get_position()
        if not self.__is_valid_position(measurement):
            return False

        if not self.has_valid_position:
            self.position = measurement
            self.__orientation_reference = measurement
            self.has_valid_position = True
            return True

        self.position = (
            self.position * (1 - self.position_filter_alpha) +
            measurement * self.position_filter_alpha)
        return True

    def get_position(self):
        """GPS 센서에서 현재 전역 위치(x, y)를 읽어 반환합니다. (Webots의 z축 → y축으로 변환)"""
        vals = self.device.getValues()
        return Position2D(vals[0] * self.multiplier, vals[2] * self.multiplier)

    def get_orientation(self):
        """
        직선 주행 구간의 기준 위치에서 현재 위치로의 방향 벡터를 이용해 진행 각도를 반환합니다.
        로봇이 충분히 이동했고 직진 중일 때만 정확합니다.
        이동이 없거나 너무 짧으면 None 반환 → PoseManager가 자이로스코프로 대체합니다.
        """
        displacement = abs(self.position.get_distance_to(self.__orientation_reference))
        if displacement >= self.orientation_min_displacement:
            angle = self.__orientation_reference.get_angle_to(self.position)
            self.__orientation_reference = self.position
            angle.normalize()
            return angle
        return None

    def reset_orientation_reference(self):
        """Start a fresh heading baseline after a turn or non-straight motion."""
        self.__orientation_reference = self.position

    @staticmethod
    def __is_valid_position(position):
        """Return True only for GPS samples that can safely enter mapping."""
        return math.isfinite(position.x) and math.isfinite(position.y)
