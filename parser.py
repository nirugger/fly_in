from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    ...


class ParseError(Exception):

    def __init__(
            self,
            line_num: int,
            message: str
       ) -> None:
        self.configuration = self.manual()

        super().__init__(
            "[ERROR]: "
            f"line {line_num}: {message}"
            # f"\n\n{self.configuration}\n\n"
        )

    def manual(self) -> str:
        return (
         "╔═══════════════════════════════════════════════════════════════╗\n"
         "║ MANUAL FOR A CORRECT USAGE OF MAPFILE CONFIGURATION : READ IT ║\n"
         "╚═══════════════════════════════════════════════════════════════╝\n"
         "                                                                 \n"
         "╔═══════════════════════ EXPECTED FORMAT FOR EACH LINE TYPE ════╗\n"
         "║ nb_drones: number                                             ║\n"
         "║ hub: name x y [metadata=value]                                ║\n"
         "║ start_hub: name x y [metadata=value]                          ║\n"
         "║ end_hub: name x y [metadata=value]                            ║\n"
         "║ connection: zone1-zone2 [metadata=value]                      ║\n"
         "╚═══════════════════════════════════════════════════════════════╝\n"
         "                                                                 \n"
         "╔════════════════════════════════════════ RULES AND CONTEXT ════╗\n"
         "║ 'nb_drones: number'                                           ║\n"
         "║ * represents the total number of drones in the map            ║\n"
         "║ - it must be the first non-comment line of the mapfile;       ║\n"
         "║ - there must be exatly one 'nb_drones:' line in the mapfile;  ║\n"
         "║ - 'number' must be a valid greater-than-zero integer          ║\n"
         "║                                                               ║\n"
         "║ 'hub: name x y [metadata=value]'                              ║\n"
         "║ 'start_hub: name x y [metadata=value]'                        ║\n"
         "║ 'end_hub: name x y [metadata=value]'                          ║\n"
         "║ * represent nodes in the map                                  ║\n"
         "║ * has name, coordinates, optional metadatas                   ║\n"
         "║ - there must be exactly one 'start_hub:' line in the mapfile  ║\n"
         "║ - there must be exactly one 'end_hub:' line in the mapfile    ║\n"
         "║ - 'name' must be unique for each hub.                         ║\n"
         "║ - 'name' can use any valid characters but dashes and spaces   ║\n"
         "║ - 'x' and 'y' must be valid positive integers                 ║\n"
         "║ - 'metadata=value' can be optionally selected as follows:     ║\n"
         "║ - 'zone' = 'normal' | 'blocked' | 'restricted' | 'priority'   ║\n"
         "║ - 'max_drones' = 'number' (greater-than-zero integer)         ║\n"
         "║ - 'color' = 'any valid string'                                ║\n"
         "║ - multiple metadatas must be separated with spaces            ║\n"
         "║ - 'start_hub:' and 'end_hub:' will set 'max_drone' value to   ║\n"
         "║   'nb_drones' if needed.                                      ║\n"
         "║                                                               ║\n"
         "║ 'connection: zone1-zone2'                                     ║\n"
         "║ * represents an edge in the map                               ║\n"
         "║ - 'zone1' and 'zone2' must be a valid 'name' value            ║\n"
         "║ - 'zone1' and 'zone2' must not have the same name             ║\n"
         "║ - there cannot be duplicates connections (connection: a-b is  ║\n"
         "║   considered a duplicate of b-a                               ║\n"
         "║ - 'metadata=value' can be optionally selected as follows:     ║\n"
         "║ - 'max_link_capacity' = 'number' (greater-than-zero integer)  ║\n"
         "╚═══════════════════════════════════════════════════════════════╝\n"
        )


class ParseWarning(Exception):

    def __init__(
            self,
            line_num: int,
            message: str
       ) -> None:

        super().__init__(
            "[WARNING]: "
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

    def parse(
            self
       ) -> dict[str, Any]:
        try:
            self._read_file()
            self._parse_lines()
            self._validate()
            return {
                "nb_drones": self.nb_drones,
                "zones": self.zones,
                "connections": self.connections
            }
        except ParseError as e:
            print(str(e))

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

            if line.startswith(("start_hub: ", "end_hub: ", "hub: ")):
                self._parse_zone(line_num, line)

            elif line.startswith("connection: "):
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

        data_metadata = line.split('[')

        if len(data_metadata) > 2:
            raise ParseError(
                line_num,
                "zone data format expected: "
                "'<type>: <name> <x> <y> "
                "<[metadata1=value metadata2=value ...]>'"
            )

        data = data_metadata[0].split()
        if len(data) != 4:
            raise ParseError(
                line_num,
                "zone data format expected: "
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
                    "zone name can use any valid character "
                    "but dashes and spaces"
                )

        try:
            x = int(data[2])
            y = int(data[3])
        except ValueError:
            raise ParseError(
                line_num,
                "zone coordinates must be valid integers"
            )

        unsplit_metadata = (
            data_metadata[1].strip().split(']')
            if len(data_metadata) == 2
            else []
        )

        if len(unsplit_metadata) == 2:
            if unsplit_metadata[1] != '':
                raise ParseError(
                        line_num,
                        f"invalid metadata format: '{unsplit_metadata}'"
                    )
            unsplit_metadata.remove('')

        metadata = (
            unsplit_metadata[0].strip().split()
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
                    int(parts[1].strip())
                except ValueError:
                    print(parts[1])
                    raise ParseError(
                        line_num,
                        "'max_drones' value must be a valid integer"
                    )

                if int(parts[1].strip()) < 1:
                    raise ParseError(
                        line_num,
                        "'max_drones' value must be a positive integer"
                    )

            meta_dict[parts[0]] = parts[1]

        max_drones = int(meta_dict.get("max_drones", "1"))
        if data[0] in special_hub:
            if (meta_dict.get("max_drones")
                    and max_drones < self.nb_drones):
                try:
                    raise ParseWarning(
                        line_num,
                        f"'max_drones' value ({max_drones}) "
                        "for 'start_hub' and 'end_hub' shouldn't be "
                        f"lesser than 'nb_drones' value ({self.nb_drones})"
                    )
                except ParseWarning as e:
                    print(e)

            if max_drones < self.nb_drones:
                max_drones = self.nb_drones

        self.zones[data[1]] = {
            "line_num": line_num,
            "name": data[1],
            "type": meta_dict.get("zone", "normal"),
            "x": x,
            "y": y,
            "max_drones": max_drones,
            "color": meta_dict.get("color", "grey"),
            "is_start": data[0] == "start_hub:",
            "is_end": data[0] == "end_hub:",
        }

    def _parse_connection(self, line_num: int, line: str) -> None:

        valid_metadata = ["max_link_capacity"]

        data_metadata = line.strip().split('[')

        if len(data_metadata) > 2:
            raise ParseError(
                line_num,
                "connection data format expected: "
                "'<type>: <name1>-<name2> <[metadata=value]>'"
            )

        data = data_metadata[0].split()
        if len(data) != 2 or len(data[1].split('-')) != 2:
            raise ParseError(
                line_num,
                "connection data format expected: "
                "'<type>: <name1>-<name2>'"
            )

        zone_a, zone_b = data[1].split('-')
        if zone_a == zone_b:
            raise ParseError(
                line_num,
                f"can't connect a zone to itself ({zone_a}-{zone_b})"
            )

        metadata = (
            data_metadata[1].rstrip(']').split()
            if len(data_metadata) == 2
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
                    err_line = int(item["line_num"])
                    raise ParseError(
                        err_line,
                        "can't be more than 1 occurrence of "
                        "special hub 'start_hub' "
                        f"(first occurrence in line {start_hub_line})"
                    )

            if item['is_end']:
                if not found_end:
                    found_end = True
                    end_hub_line = item["line_num"]
                else:
                    err_line = int(item["line_num"])
                    raise ParseError(
                        err_line,
                        "can't be more than 1 occurrence of "
                        "special hub 'end_hub' "
                        f"(first occurrence in line {end_hub_line})"
                    )

        if not found_start:
            raise ParseError(
                404,
                "'start_hub' not found."
            )

        if not found_end:
            raise ParseError(
                404,
                "'end_hub' not found."
            )

        connected_zones: list[set[str | int]] = []
        for item in self.connections:
            if item["zone_a"] not in self.zones:
                err_line = int(item["line_num"])
                raise ParseError(
                    err_line,
                    f"zone '{item['zone_a']}' is not a valid zone"
                )

            if item["zone_b"] not in self.zones:
                err_line = int(item["line_num"])
                raise ParseError(
                    err_line,
                    f"zone '{item['zone_b']}' is not a valid zone"
                )

            connection_set = {item["zone_a"], item["zone_b"]}
            if connection_set in connected_zones:
                err_line = int(item["line_num"])
                raise ParseError(
                    err_line,
                    "the same connection must not appear more than once "
                    "('a-b' and 'b-a' are considered duplicates)"
                )
            connected_zones.append(connection_set)
