"""Simplified Servo class for 6-wheel rover steering using TCA9548A + PCA9685.

Matches the simple interface you showed (state + fixed movement patterns) but
actually drives hardware when available. Falls back to dry-run printing when
libraries/hardware aren't present (e.g. on Windows).

Wheel index order: [FL, FR, ML, MR, RL, RR]

Angle model:
  - Standard hobby servos: 0..180 degrees (mechanical range). Your example had
    values like 315 which exceed 180; those likely represent -45 (i.e. 315° in
    a 0-360 wrap). Here we normalize >180 by angle % 360 and then, if result >180,
    map into 0-180 by reflecting or clamping (simplest: wrap and clamp).
  - Adjust PATTERNS below to your real mechanical steering geometry.
"""

from __future__ import annotations

import time
from typing import List, Sequence

try:  # Hardware imports
    import board  # type: ignore
    import adafruit_tca9548a  # type: ignore
    from adafruit_servokit import ServoKit  # type: ignore
    _HW_AVAILABLE = True
except Exception:  # noqa: BLE001 - broad to allow Windows dev
    _HW_AVAILABLE = False
    board = adafruit_tca9548a = ServoKit = None  # type: ignore


# Movement angle patterns (modify as needed). All lists length 6.
# Use centered (90) as straight orientation; offsets applied relative to center.
CENTER = 90
PATTERNS = {
    "STOP": [CENTER] * 6,
    "FORWARD": [CENTER] * 6,
    "BACKWARD": [CENTER] * 6,  # Steering same; actual motion via drive motors
    # Crab / strafe: wheels turned to enable lateral motion if drive design supports it
    "STRAFE_LEFT": [CENTER - 45, CENTER + 45, CENTER - 45, CENTER + 45, CENTER - 45, CENTER + 45],
    "STRAFE_RIGHT": [CENTER + 45, CENTER - 45, CENTER + 45, CENTER - 45, CENTER + 45, CENTER - 45],
    # Diagonals (tune for your geometry)
    "DIAGONAL_LEFT_FORWARD": [CENTER, CENTER - 30, CENTER, CENTER - 30, CENTER, CENTER - 30],
    "DIAGONAL_RIGHT_FORWARD": [CENTER + 30, CENTER, CENTER + 30, CENTER, CENTER + 30, CENTER],
    # Spin (approximate: toe wheels inward/outward). Adjust to minimize scrub.
    "SPIN_LEFT": [CENTER - 45, CENTER + 45, CENTER + 45, CENTER - 45, CENTER - 45, CENTER + 45],
    "SPIN_RIGHT": [CENTER + 45, CENTER - 45, CENTER - 45, CENTER + 45, CENTER + 45, CENTER - 45],
}


class Servo:
    def __init__(
        self,
        *,
        tca_channel: int = 2,  # TCA9548A channel for PCA9685 Change It Later
        channels: Sequence[int] = (0, 1, 2, 3, 4, 5),
        pulse_range=(500, 2500),
        dry_run: bool | None = None,
        smooth_step: int = 3,          # degrees per smoothing increment
        smooth_delay: float = 0.02,     # seconds between increments
    ) -> None:
        # Initial state & config
        self.state: str = "STOP"
        self._channels = list(channels)
        self.wheels: List[int] = list(PATTERNS[self.state])  # current absolute angles
        self._smooth_step = max(1, int(smooth_step))
        self._smooth_delay = max(0.0, float(smooth_delay))

        # Determine dry run
        if dry_run is None:
            dry_run = not _HW_AVAILABLE
        self._dry = dry_run

        if not self._dry:
            try:
                i2c = board.I2C()
                tca = adafruit_tca9548a.TCA9548A(i2c)
                pca_bus = tca[tca_channel]
                self._kit = ServoKit(channels=16, i2c=pca_bus)
                for ch in self._channels:
                    self._kit.servo[ch].set_pulse_width_range(*pulse_range)
            except Exception as e:  # noqa: BLE001
                print(f"[Servo] Hardware init failed ({e}); switching to dry-run mode.")
                self._dry = True
                self._kit = None  # type: ignore
        else:
            self._kit = None  # type: ignore

        # Apply initial STOP pattern
        self._apply_to_hardware()

    # ---------------- Core helpers -----------------
    def _normalize_angle(self, a: int) -> int:
        # Wrap into 0..359 then clamp to 0..180 (simple approach)
        a = int(a) % 360
        if a > 180:
            # Map >180 into an approximate reflected range (optional refinement)
            a = 360 - a
        return max(0, min(180, a))

    def set_angles(self, angles: Sequence[int], *, smooth: bool = True) -> None:
        """Set all 6 wheel angles.

        angles: sequence length 6
        smooth: if True, ramp gradually from current to target to reduce stress
        """
        if len(angles) != 6:
            raise ValueError("Must provide 6 angles")
        target = [self._normalize_angle(a) for a in angles]
        if not smooth:
            self.wheels = target
            self._apply_to_hardware()
            return

        # Ramped transition
        current = [int(a) for a in self.wheels]
        done = False
        while not done:
            done = True
            for i, tgt in enumerate(target):
                diff = tgt - current[i]
                if abs(diff) > self._smooth_step:
                    current[i] += self._smooth_step * (1 if diff > 0 else -1)
                    done = False
                else:
                    current[i] = tgt
            self.wheels = current.copy()
            self._apply_to_hardware()
            if not done:
                time.sleep(self._smooth_delay)

    def _apply_to_hardware(self) -> None:
        if self._dry:
            print(f"[{self.state}] (dry-run) Wheels -> {self.wheels}")
            return
        for angle, ch in zip(self.wheels, self._channels):
            self._kit.servo[ch].angle = angle  # type: ignore[attr-defined]

    # ---------------- Movement states -----------------
    def _set_state(self, new_state: str) -> None:
        if new_state not in PATTERNS:
            raise ValueError(f"Unknown state '{new_state}'")
        self.state = new_state
        self.set_angles(PATTERNS[new_state])

    def stop(self):
        self._set_state("STOP")

    def forward(self):
        self._set_state("FORWARD")

    def backward(self):
        self._set_state("BACKWARD")

    def strafe_left(self):
        self._set_state("STRAFE_LEFT")

    def strafe_right(self):
        self._set_state("STRAFE_RIGHT")

    def diagonal_left_forward(self):
        self._set_state("DIAGONAL_LEFT_FORWARD")

    def diagonal_right_forward(self):
        self._set_state("DIAGONAL_RIGHT_FORWARD")

    def spin_left(self):
        self._set_state("SPIN_LEFT")

    def spin_right(self):
        self._set_state("SPIN_RIGHT")

    # Utility
    def current(self) -> List[int]:
        return list(self.wheels)


if __name__ == "__main__":
    rover_servo = Servo()
    rover_servo.forward()
    rover_servo.strafe_left()
    rover_servo.spin_right()
    rover_servo.stop()
