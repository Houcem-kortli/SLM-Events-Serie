# encoding: utf-8
import json
import math
import csv
from datetime import datetime

ZIG_ZAG_XY = "ZIG_ZAG_XY"
ZIG_ZAG_X = "ZIG_ZAG_X"
ONE_DIRECTION_XY = "ONE_DIRECTION_XY"
ONE_DIRECTION_X = "ONE_DIRECTION_X"
SPIRAL = "SPIRAL"


def read_config():
    with open('./config.json') as f:
        return json.load(f)


def write_to_csv(points, filetype):
    now = datetime.now()
    folder = now.strftime('%Y-%m-%d')
    filename = now.strftime('%H-%M-%S')
    with open('./output/{folder}-{filename}_es_{filetype}.csv'.format(folder=folder, filename=filename, filetype=filetype), 'w+') as f:
        writer = csv.writer(f)
        for p in points:
            writer.writerow(p)


def print_points(points):
    for p in points:
        print(p)
        print('\n')


def move_horizontally_zig_zag(t, max_x, max_y, speed, layer_index, interline_gap, power):
    points = [(t, 0, 0, layer_index, power)]
    direction = 'left'
    max_lines = int(max_y / interline_gap) + 1

    def move_up(point):
        t, x, y, _, _ = point
        delta_t = interline_gap / float(speed)
        return (t + delta_t, x, round(y + interline_gap, 2), layer_index, power)

    def move_left(point):
        t, x, y, _, _ = point
        delta_t = max_x * (1 / float(speed))
        return (t + delta_t, max_x, y, layer_index, 0)

    def move_right(point):
        t, x, y, _, _ = point
        delta_t = max_x * (1 / float(speed))
        return (t + delta_t, 0, y, layer_index, 0)

    for _ in range(0, max_lines):
        last_point = points[-1]
        if direction == 'left':
            last_point = move_left(last_point)
            direction = 'right'
        else:
            last_point = move_right(last_point)
            direction = 'left'

        points.append(last_point)
        if (last_point[2] + interline_gap) <= max_y:
            points.append(move_up(last_point))
    return points


def move_vertically_zig_zag(t, max_x, max_y, speed, layer_index, interline_gap, power):
    # points = [compute_origin(t, powder_diposit_time, layer_index, power)]
    points = [(t, 0, 0, layer_index, power)]
    direction = 'up'
    max_lines = int(max_x / interline_gap) + 1

    def move_up(point):
        t, x, y, _, _ = point
        delta_t = max_y * (1 / float(speed))
        return (t + delta_t, x, max_y, layer_index, 0)

    def move_down(point):
        t, x, y, _, _ = point
        delta_t = max_y * (1 / float(speed))
        return (t + delta_t, x, 0, layer_index, 0)

    def move_right(point):
        t, x, y, _, _ = point
        delta_t = interline_gap / float(speed)
        return (t + delta_t, round(x + interline_gap, 2), y, layer_index, power)

    for i in range(0, max_lines):
        last_point = points[-1]
        if direction == 'up':
            last_point = move_up(last_point)
            direction = 'down'
        else:
            last_point = move_down(last_point)
            direction = 'up'

        points.append(last_point)
        if (last_point[1] + interline_gap) <= max_x:
            points.append(move_right(last_point))
    # move back to origin (0, 0)
    # points.append(move_to_origin(last_point, speed, layer_index))
    return points


def move_horizontally_one_dir(t, max_x, max_y, speed, layer_index, interline_gap, power):
    points = [(t, 0, 0, layer_index, power)]
    max_lines = int(max_y / interline_gap) + 1

    def move_left(point):
        t, x, y, _, _ = point
        delta_t = max_x * (1 / float(speed))
        return (t + delta_t, max_x, y, layer_index, 0)

    def move_next_line(point):
        t, x, y, _, _ = point
        delta_t = max_x / float(speed)
        return (t + delta_t, 0, round(y + interline_gap, 2), layer_index, power)

    for _ in range(0, max_lines):
        last_point = points[-1]
        last_point = move_left(last_point)

        points.append(last_point)
        if (last_point[2] + interline_gap) <= max_y:
            points.append(move_next_line(last_point))
    return points


def move_vertically_one_dir(t, max_x, max_y, speed, layer_index, interline_gap, power):
    points = [(t, 0, 0, layer_index, power)]
    max_lines = int(max_x / interline_gap) + 1

    def move_up(point):
        t, x, y, _, _ = point
        delta_t = max_y / float(speed)
        return (t + delta_t, x, max_y, layer_index, 0)

    def move_next_line(point):
        t, x, y, _, _ = point
        delta_t = max_y / float(speed)
        return (t + delta_t, round(x + interline_gap, 2), 0, layer_index, power)

    for _ in range(0, max_lines):
        last_point = points[-1]
        last_point = move_up(last_point)
        points.append(last_point)
        if (last_point[1] + interline_gap) <= max_x:
            points.append(move_next_line(last_point))
    return points


if __name__ == "__main__":
    config = read_config()
    max_x = config.get('max_x')
    max_y = config.get('max_y')
    max_z = config.get('max_z')
    interline_gap = config.get('interline_gap')
    layer_depth = config.get('layer_depth')
    powder_diposit_time = config.get('powder_deposit_time')
    average_layering_time = config.get('average_layering_time')
    roller_x_left = config.get('roller_x_left')
    roller_x_right = config.get('roller_x_right')
    speed = config.get('speed')
    power = config.get('puissance')
    scanning = config.get('scanning')
    points = []

    total_layers = int(max_z / layer_depth)

    # Compute laser points for all layers
    # Scanning: ZIG_ZAG_XY
    if scanning == ZIG_ZAG_XY:
        for i in range(total_layers):
            t = i * average_layering_time + powder_diposit_time
            layer_index = (i + 1) * layer_depth
            if i % 2 == 0:
                r = move_horizontally_zig_zag(t, max_x, max_y, speed,
                                              layer_index=round(layer_index, 3), interline_gap=interline_gap,
                                              power=power)
            else:
                r = move_vertically_zig_zag(t, max_x, max_y, speed,
                                            layer_index=round(layer_index, 3), interline_gap=interline_gap,
                                            power=power)
            points.extend(r)

    # Compute laser points for all layers
    # Scanning: ZIG_ZAG_X
    elif scanning == ZIG_ZAG_X:
        for i in range(total_layers):
            t = i * average_layering_time + powder_diposit_time
            layer_index = (i + 1) * layer_depth

            r = move_horizontally_zig_zag(t, max_x, max_y, speed,
                                          layer_index=round(layer_index, 3), interline_gap=interline_gap,
                                          power=power)
            points.extend(r)

    # Scanning: ONE_DIRECTION_XY
    elif scanning == ONE_DIRECTION_XY:
        for i in range(total_layers):
            t = i * average_layering_time + powder_diposit_time
            layer_index = (i + 1) * layer_depth
            if i % 2 == 0:
                r = move_horizontally_one_dir(t, max_x, max_y, speed,
                                              layer_index=round(layer_index, 3), interline_gap=interline_gap,
                                              power=power)
            else:
                r = move_vertically_one_dir(t, max_x, max_y, speed,
                                            layer_index=round(layer_index, 3), interline_gap=interline_gap,
                                            power=power)
            points.extend(r)

    # Scanning: ONE_DIRECTION_X
    elif scanning == ONE_DIRECTION_X:
        for i in range(total_layers):
            t = i * average_layering_time + powder_diposit_time
            layer_index = (i + 1) * layer_depth
            r = move_horizontally_one_dir(t, max_x, max_y, speed,
                                          layer_index=round(layer_index, 3), interline_gap=interline_gap,
                                          power=power)
            points.extend(r)

    roller_points = []
    roller_y = float(max_y) / 2

    # Compute roller points for all layers
    for i in range(total_layers):
        layer_index = round((i + 1) * layer_depth, 3)
        layer_start_time = i * average_layering_time
        roller_points.append(
            (layer_start_time, roller_x_left, roller_y, layer_index, 1))
        roller_points.append((layer_start_time + powder_diposit_time,
                              roller_x_right, roller_y, layer_index, 0))

    write_to_csv(points, 'laser')
    write_to_csv(roller_points, 'roller')
