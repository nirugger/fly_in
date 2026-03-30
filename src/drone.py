from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

if TYPE_CHECKING:
    from src.zone import Zone
    from src.connection import Connection


class DroneState(Enum):
    """Enum class for different Drone states."""

    WAITING = "waiting"
    MOVING = "moving"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"


class Drone:

    def __init__(
            self,
            drone_id: int,
            current_zone: Zone | None,
            current_connection: Connection | None,
            turns_in_transit: int,
       ) -> None:

        self.drone_id = drone_id
        self.current_zone = current_zone
        self.current_connection = current_connection
        self.turns_in_transit = turns_in_transit     # 1 o 0 se restricted
        self.state: DroneState = DroneState.WAITING  # "waiting" | "moving" | "in_transit" | "arrived"

    def is_arrived(self) -> bool:
        return self.state == DroneState.ARRIVED

    def next_zone(self) -> Zone | None:
        pass
