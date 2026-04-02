from __future__ import annotations
from typing import Any
from src.drone import Drone
from src.zone import Zone
from src.connection import Connection


class Builder:

    def __init__(
            self,
            raw_data: dict[str, Any]
       ) -> None:

        self.raw_data = raw_data
        self.build_zone_list()
        self.build_connection_list()
        self.build_adjacency()

    def build_drone_list(self) -> list[Drone]:

        drone_list: list[Drone] = []
        nb_drones = int(self.raw_data["nb_drones"])

        for id in range(1, nb_drones + 1):
            drone_list.append(Drone(id))
        return drone_list

    def build_zone_list(self) -> list[Zone]:

        zone_list: list[Zone] = []
        zone_data: dict[str, Any] = self.raw_data["zones"]

        for item in zone_data.values():
            if item['type'] != "blocked":
                zone_list.append(Zone(
                    name=item['name'],
                    zone_type=item['type'],
                    x=item['x'],
                    y=item['y'],
                    is_start=item['is_start'],
                    is_end=item['is_end'],
                    max_drones=item['max_drones'],
                    color=item['color']
                ))
        return zone_list

    def build_connection_list(self) -> list[Connection]:

        zone_list: list[Zone] = self.build_zone_list()
        connection_list: list[Connection] = []
        connection_data: list[Any] = self.raw_data["connections"]
        for item in connection_data:
            zone_a, zone_b = "", ""
            for zone in zone_list:
                if zone.name == item['zone_a']:
                    zone_a = zone
                if zone.name == item['zone_b']:
                    zone_b = zone

            if zone_a == "" or zone_b == "":
                continue

            connection_list.append(Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                max_link_capacity=item['max_link_capacity']
            ))
        return connection_list

    def build_adjacency(self) -> dict[Zone, list[Connection]]:

        zone_list = self.build_zone_list()
        connection_list = self.build_connection_list()

        return {
            zone: [connection
                   for connection in connection_list
                   if connection.zone_a.name == zone.name
                   or connection.zone_b.name is zone.name]
            for zone in zone_list
        }
