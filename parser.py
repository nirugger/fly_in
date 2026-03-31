from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...


class ParseError(Exception):

    def __init__(
            self,
            line_num: int,
            message: str
       ) -> None:

        super().__init__(
            "[ERROR]: "
            f"line {line_num}: {message}"
        )


class Parser:

    def __init__(
            self,
            path: str
       ) -> None:

        self.path = path
        self.lines: list[tuple[int, str]] = []
        self.nb_drones: int = 0
        self.zones: dict[str, dict[str, str | int]] = {}
        self.connections: list[dict[str, str | int]] = []

    def parse(self) -> dict:
        self._read_file()
        self._parse_lines()
        self._validate()
        return {
            "nb_drones": self.nb_drones,
            "zones": self.zones,
            "connections": self.connections
        }

    def _read_file(self) -> None:

        with open(self.path, 'r') as f:
            self.lines = [
                (i + 1, line.strip())
                for i, line in enumerate(f.read().split('\n'))
                if line.strip() and not line.strip().startswith('#')
            ]

    def _parse_lines(self) -> None:

        first_line_num, first_line = self.lines[0]
        self._parse_nb_drones(first_line_num, first_line)

        for line_num, line in self.lines[1:]:

            if line.startswith(("start_hub:", "end_hub:", "hub:")):
                self._parse_zone(line_num, line)

            elif line.startswith("connection:"):
                self._parse_connection(line_num, line)

            else:
                raise ParseError(
                    line_num,
                    f"unrecognized line format: '{line}'"
                )

    def _parse_nb_drones(self, line_num: int, line: str) -> None:

        parts = line.split()

        if len(parts) != 2 or parts[0] != 'nb_drones:':
            raise ParseError(
                line_num,
                "expected 'nb_drones: <positive_integer>'"
            )

        try:
            n = int(parts[1])
        except ValueError:
            raise ParseError(
                line_num,
                "nb_drones must be a positive integer"
            )

        if n <= 0:
            raise ParseError(
                line_num,
                "nb_drones must be a positive integer"
            )

        self.nb_drones = n

    def _parse_zone(self, line_num: int, line: str) -> None:

        valid_metadata = ["zone", "color", "max_drones"]
        valid_zone_type = ["normal", "blocked", "restricted", "priority"]
        special_hub = ["start_hub:", "end_hub:"]

        raw_data = line.split('[')

        if len(raw_data) > 2:
            raise ParseError(
                line_num,
                "Zone data format expected: "
                "'<type>: <name> <x> <y> <[metadatas=values]>'"
            )

        data = raw_data[0].split()
        if len(data) != 4:
            raise ParseError(
                line_num,
                "Zone data format expected: "
                "'<type>: <name> <x> <y>'"
            )

        if data[1] in self.zones:
            raise ParseError(
                line_num,
                f"duplicate zone name '{data[1]}'"
            )

        for c in data[1]:
            if not c.isprintable() or c.isspace() or c == '-':
                raise ParseError(
                    line_num,
                    "Zone name must use any valid character "
                    "BUT dashes and spaces"
                )

        try:
            x = int(data[2])
            y = int(data[3])
        except ValueError:
            raise ParseError(
                line_num,
                "Zone coordinates must be valid integers"
            )

        metadata = (
            raw_data[1].rstrip(']').split()
            if len(raw_data) == 2
            else []
        )

        meta_dict = {}
        for item in metadata:
            parts = item.split('=')
            if len(parts) != 2:
                raise ParseError(
                    line_num,
                    f"invalid metadata format: '{item}'"
                )

            if parts[0] not in valid_metadata:
                raise ParseError(
                    line_num,
                    f"invalid metadata value: '{parts[0]}'\n"
                    f"(accepted metadata values: {valid_metadata})"
                )

            if parts[0] == "zone":
                if parts[1] not in valid_zone_type:
                    raise ParseError(
                        line_num,
                        f"invalid zone type: '{parts[1]}'\n"
                        f"(accepted zone types: {valid_zone_type})"
                    )

            elif parts[0] == "max_drones":
                try:
                    int(parts[1])
                except ValueError:
                    raise ParseError(
                        line_num,
                        "'max_drones' value must be a valid integer"
                    )

                if int(parts[1]) < 1:
                    raise ParseError(
                        line_num,
                        "'max_drones' value must be a positive integer"
                    )

            meta_dict[parts[0]] = parts[1]

        max_drones = int(meta_dict.get("max_drones", "1"))
        if data[0] in special_hub:
            if max_drones < self.nb_drones and max_drones != 1:
                raise ParseError(
                    line_num,
                    "max_drones in start_hub and end_hub "
                    "can't be lesser than nb_drones"
                )
            if max_drones == 1:
                max_drones = self.nb_drones

        self.zones[data[1]] = {
            "line_num": line_num,
            "type": meta_dict.get("zone", "normal"),
            "x": x,
            "y": y,
            "max_drones": max_drones,
            "color": meta_dict.get("color"),
            "is_start": data[0] == "start_hub:",
            "is_end": data[0] == "end_hub:",
        }

    def _parse_connection(self, line_num: int, line: str) -> None:

        valid_metadata = ["max_link_capacity"]

        raw_data = line.split('[')

        if len(raw_data) > 2:
            raise ParseError(
                line_num,
                "Connection data format expected: "
                "'<type>: <name1>-<name2> <[metadata=value]>'"
            )

        data = raw_data[0].split()
        if len(data) != 2 or len(data[1].split('-')) != 2:
            raise ParseError(
                line_num,
                "Connection data format expected: "
                "'<type>: <name1>-<name2>'"
            )

        zone_a, zone_b = data[1].split('-')
        if zone_a == zone_b:
            raise ParseError(
                line_num,
                f"can't connect a Zone to itself ({zone_a}-{zone_b})"
            )

        metadata = (
            raw_data[1].rstrip(']').split()
            if len(raw_data) == 2
            else []
        )

        max_link_capacity = 1
        for item in metadata:
            parts = item.strip().split('=')
            if len(parts) != 2:
                raise ParseError(
                    line_num,
                    "expected metadata format: <[metadata=value]>"
                )

            if parts[0] not in valid_metadata:
                raise ParseError(
                    line_num,
                    f"invalid connection metadata: '{parts[0]}'\n"
                    f"(accepted connection metadatas: {valid_metadata})"
                )

            if parts[0] == "max_link_capacity":
                try:
                    max_link_capacity = int(parts[1])
                except ValueError:
                    raise ParseError(
                        line_num,
                        "'max_link_capacity' value must be a valid integer"
                    )

                if max_link_capacity < 1:
                    raise ParseError(
                        line_num,
                        "'max_link_capacity' value must be a positive integer"
                    )

        self.connections.append({
            "line_num": line_num,
            "zone_a": zone_a,
            "zone_b": zone_b,
            "max_link_capacity": max_link_capacity
        })

    def _validate(self) -> None:

        found_start = False
        found_end = False

        for item in self.zones.values():

            if item["is_start"]:
                if not found_start:
                    found_start = True
                    start_hub_line = item["line_num"]
                else:
                    raise ParseError(
                        item["line_num"],
                        "can't be more than 1 occurrence of "
                        "special hub 'start_hub' "
                        f"(first occurrence in line {start_hub_line})"
                    )

            if item['is_end']:
                if not found_end:
                    found_end = True
                    end_hub_line = item["line_num"]
                else:
                    raise ParseError(
                        item["line_num"],
                        "can't be more than 1 occurrence of "
                        "special hub 'end_hub' "
                        f"(first occurrence in line {end_hub_line})"
                    )
            del item["line_num"]

        if not found_start:
            raise ParseError(
                0,
                "can't be less than 1 occurrence of "
                "special hub 'start_hub'"
            )

        if not found_end:
            raise ParseError(
                0,
                "can't be less than 1 occurrence of "
                "special hub 'end_hub'"
            )

        zone_names = list(self.zones.keys())
        connected_zones: list[set[str]] = []
        for item in self.connections:
            if item["zone_a"] not in zone_names:
                raise ParseError(
                    item["line_num"],
                    f"zone '{item['zone_a']}' is not a valid zone"
                )

            if item["zone_b"] not in zone_names:
                raise ParseError(
                    item["line_num"],
                    f"zone '{item['zone_b']}' is not a valid zone"
                )

            connection_set = {item["zone_a"], item["zone_b"]}
            if connection_set in connected_zones:
                raise ParseError(
                    item["line_num"],
                    "the same connection must not appear more than once"
                    "('a-b' and 'b-a' are considered duplicates)"
                )
            connected_zones.append(connection_set)
            del item["line_num"]
