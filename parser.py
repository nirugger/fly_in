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
        self.zones: dict[str, dict] = {}
        self.connections: list[dict] = []

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
                    f"unrecognized line: '{line}'"
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

        raw_data = line.split('[')

        if len(raw_data) > 2:
            raise ParseError(
                line_num,
                "Zone data format expected: "
                "'<type>: <name> <x> <y> <[optional_datas=values]>'"
            )

        data = raw_data[0].split()
        if len(data) != 4:
            raise ParseError(
                line_num,
                "Zone data format expected: "
                "'<type> <name> <x> <y>'"
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
            # elif parts[0] == "color":
            #     if not isinstance(parts[1], str):
            #         raise ParseError(
            #             line_num,
            #             f"invalid color choice: '{parts[1]}'"
            #             f"(accepted colors: <any_string>)"
            #         )
            elif parts[0] == "max_drones":
                try:
                    max_drones = int(parts[1])
                except ValueError:
                    raise ParseError(
                        line_num,
                        "'max drones' value must be a valid integer"
                    )
                if max_drones < 1:
                    raise ParseError(
                        line_num,
                        "'max drones' value must be a positive integer"
                    )
            else:
                pass
            meta_dict[parts[0]] = parts[1]

        self.zones[data[1]] = {
            "type": meta_dict.get("zone", "normal"),
            "x": x,
            "y": y,
            "max_drones": int(meta_dict.get("max_drones", "1")),
            "color": meta_dict.get("color"),
            "is_start": data[0] == "start_hub:",
            "is_end": data[0] == "end_hub:",
        }
