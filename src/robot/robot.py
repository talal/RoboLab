import time
from typing import Dict, List, Tuple

from communication.communication import Communication, MessageType
from logger import get_logger
from planet.planet import Planet
from robot.movement.movement import MovementController
from robot.odometry import Odometry
from utils.common import Direction, flip_direction, PathStatus


class Robot:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.planet = Planet()
        self.odometry = Odometry()
        self.communication: Communication = None
        self.movement_controller = MovementController()

        self.temporary_target: Tuple[int, int] = None
        self.server_corrected_direction: Direction = None
        self.unfinished_nodes: List[Tuple[int, int]] = list()
        self.scanned_directions: Dict[Tuple[int, int], List[Direction, ...]] = dict()
        self.blocked_paths: Dict[Tuple[int, int], List[Direction, ...]] = dict()

        self.logger.debug("=" * 100)

    def get_ready(self, mqtt_client):
        self.movement_controller.color_sensor.calibrate_rgb()
        time.sleep(5)
        self.movement_controller.pid_controller.calibrate()

        # go to first node
        self.movement_controller.travel_vertex()
        time.sleep(1)

        # connect to mothership and initialize Odometry
        self.communication = Communication(mqtt_client)
        self.communication.send_ready_message()
        time.sleep(1)
        self.__process_message_queue()  # this will also set Odometry's start parameters
        time.sleep(2)

    def start_exploration(self):
        while True:
            print("\n" + "===================")
            print(
                f"current_coordinates={self.odometry.current_coordinates} direction={self.odometry.current_direction}, previous coordinates={self.odometry.previous_coordinates} direction={self.odometry.previous_direction}"
            )
            print(f"temporary_target={self.temporary_target}")
            print(f"unfinished_nodes={self.unfinished_nodes}")
            print(f"scanned_directions={self.scanned_directions}")
            print(f"blocked_paths={self.blocked_paths}")

            current_coordinates = self.odometry.current_coordinates
            if current_coordinates == self.planet.target:
                self.communication.send_target_reached_message()
                break
            if current_coordinates == self.temporary_target:
                self.temporary_target = None
            if current_coordinates in self.scanned_directions:
                d = flip_direction(self.odometry.current_direction)
                if d in self.scanned_directions[current_coordinates]:
                    i = self.scanned_directions[current_coordinates].index(d)
                    del self.scanned_directions[current_coordinates][i]

            for k, v in self.scanned_directions.items():
                if len(v) == 0:
                    if k in self.unfinished_nodes:
                        i = self.unfinished_nodes.index(k)
                        del self.unfinished_nodes[i]

            target_direction = self.__get_target_direction()
            if not target_direction:
                self.communication.send_exploration_completed_message()
                break

            # tell server about the chosen target
            self.communication.send_path_select_message((current_coordinates, target_direction))
            time.sleep(1)
            self.__process_message_queue()

            if self.server_corrected_direction:
                target_direction = self.server_corrected_direction
                self.server_corrected_direction = None

            if current_coordinates in self.blocked_paths:
                if target_direction in self.blocked_paths[current_coordinates]:
                    if current_coordinates in self.scanned_directions:
                        if target_direction in self.scanned_directions[current_coordinates]:
                            i = self.scanned_directions[current_coordinates].index(target_direction)
                            del self.scanned_directions[current_coordinates][i]
                    continue

            if target_direction != self.odometry.current_direction:
                print(
                    f"stop_direction_after_scan={self.odometry.current_direction} and target_direction={target_direction}"
                )
                print(
                    f"\n inside rotation current={self.odometry.current_direction}, rotating to={target_direction} \n"
                )
                self.movement_controller.rotate_to_chosen_direction(
                    self.odometry.current_direction, target_direction
                )

            if current_coordinates in self.scanned_directions:
                if target_direction in self.scanned_directions[current_coordinates]:
                    i = self.scanned_directions[current_coordinates].index(target_direction)
                    del self.scanned_directions[current_coordinates][i]
                    print(
                        f"\n deleted {target_direction} from scanned_directions[{current_coordinates}] \n"
                    )

            print(f"\n going to {target_direction} from {current_coordinates} \n")
            # travel until the next node
            _, path_status, positions_list = self.movement_controller.travel_vertex()
            time.sleep(1)

            # get new direction and coordinates
            self.odometry.handle(self.odometry.current_direction, path_status, positions_list)
            start = (self.odometry.previous_coordinates, self.odometry.previous_direction)
            target = (
                self.odometry.current_coordinates,
                flip_direction(self.odometry.current_direction),
            )

            if path_status == PathStatus.BLOCKED:
                if self.odometry.previous_coordinates in self.blocked_paths:
                    self.blocked_paths[self.odometry.previous_coordinates].append(
                        self.odometry.previous_direction
                    )
                else:
                    self.blocked_paths[self.odometry.previous_coordinates] = [
                        self.odometry.previous_direction
                    ]

            # tell server about the travelled path
            self.communication.send_path_message(start, target, path_status)
            self.__process_message_queue()

            print(
                f"current_coordinates={self.odometry.current_coordinates} direction={self.odometry.current_direction}, previous coordinates={self.odometry.previous_coordinates} direction={self.odometry.previous_direction}"
            )
            print(f"unfinished_nodes={self.unfinished_nodes}")
            print(f"unexplored_directions={self.scanned_directions}")
            print(f"blocked_paths={self.blocked_paths}")
            print("===================" + "\n")
            self.logger.debug(f"unfinished nodes={self.unfinished_nodes}")
            self.logger.debug(f"unexplored directions={self.scanned_directions}")
            time.sleep(3)

        # out of the loop
        self.__process_message_queue()

    def __get_target_direction(self):
        current_coordinates = self.odometry.current_coordinates
        if self.planet.target:
            target_list = self.planet.shortest_path(current_coordinates, self.planet.target)
            if target_list:
                t = target_list.pop(0)
                return t[1]

        if self.temporary_target:
            target_coordinates = self.temporary_target
            target_list = self.planet.shortest_path(current_coordinates, target_coordinates)
            if target_list:
                t = target_list.pop(0)
                return t[1]

        if current_coordinates not in self.scanned_directions:
            possible_directions, stop_direction_after_scan = self.movement_controller.scan_for_paths(
                self.odometry.current_direction
            )
            self.odometry.current_direction = stop_direction_after_scan
            time.sleep(0.5)
            self.scanned_directions[current_coordinates] = possible_directions
            if len(possible_directions) > 0:
                self.unfinished_nodes.append(current_coordinates)
                t = possible_directions.pop()
                return t

        possible_directions = self.scanned_directions[current_coordinates]
        if len(possible_directions) > 0:
            t = possible_directions.pop()
            return t
        elif (len(self.unfinished_nodes) != 0) and (current_coordinates in self.unfinished_nodes):
            i = self.unfinished_nodes.index(current_coordinates)
            del self.unfinished_nodes[i]

        if len(self.unfinished_nodes) > 0:
            target_coordinates = self.unfinished_nodes[len(self.unfinished_nodes) - 1]
            target_list = self.planet.shortest_path(current_coordinates, target_coordinates)
            if target_list:
                t = target_list.pop(0)
                return t[1]

    def __process_message_queue(self):
        """ This function blocks until all messages have been processed """
        while True:
            if len(self.communication.message_queue) > 0:
                self.__communication_helper(data=self.communication.handle())
            time.sleep(2)
            if len(self.communication.message_queue) == 0:
                break

    def __communication_helper(self, data):
        if not data:
            return

        msg_type = data[0]
        if msg_type == MessageType.PLANET:
            start = data[1]
            self.odometry.current_coordinates = start
            self.odometry.current_direction = Direction.NORTH

        if msg_type == MessageType.PATH_SELECT:
            self.server_corrected_direction = data[1]

        if (msg_type == MessageType.PATH) or (msg_type == MessageType.PATH_UNVEILED):
            start = data[1]
            target = data[2]
            status = data[3]
            weight = data[4]

            if msg_type == MessageType.PATH:
                self.odometry.current_coordinates = target[0]
                self.odometry.current_direction = flip_direction(target[1])
                self.odometry.previous_coordinates = start[0]
                self.odometry.previous_direction = start[1]

            if status == PathStatus.BLOCKED:
                weight = -1
                coord = start[0]
                direc = start[1]
                if coord in self.blocked_paths:
                    self.blocked_paths[coord].append(direc)
                else:
                    self.blocked_paths[coord] = [direc]

            self.planet.add_path(start, target, weight)

        if msg_type == MessageType.TARGET:
            target = data[1]
            self.planet.target = target

        if msg_type == MessageType.DONE:
            m = data[1]
            print("\n" + m + "\n")
