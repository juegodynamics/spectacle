from manim import *


def as_point(*num_list_or_val) -> np.ndarray:
    num_list = num_list_or_val
    if len(num_list_or_val) == 0 and type(num_list_or_val[0]) == list:
        num_list = num_list_or_val[0]
    z = 0
    if len(num_list) >= 3:
        z = num_list[2]
    return np.array([num_list[0], num_list[1], z])


def get_polar_angle(start=LEFT, end=RIGHT) -> float:
    diff = end - start
    return np.angle(diff[0] + diff[1] * 1j)


def get_unit_for_angle(angle=PI / 3) -> np.ndarray:
    return as_point(np.cos(angle), np.sin(angle))


def diff_length(start=LEFT, end=RIGHT) -> float:
    return np.linalg.norm(end - start)


def interpolate_points(start=LEFT, end=RIGHT, alpha=0.5) -> np.ndarray:
    angle = get_polar_angle(start, end)
    return start + alpha * diff_length(start, end) * get_unit_for_angle(angle)


def get_wavy_curve_points(start=LEFT, end=RIGHT, width=0.5):
    mid = midpoint(start, end)

    diff = end - start
    theta = np.angle(diff[0] + diff[1] * 1j)
    perp = np.array([-np.sin(theta), np.cos(theta), 0])

    radius = width / 2

    top_control = mid + radius * perp
    btm_control = mid - radius * perp
    return [start, top_control, btm_control, end]
