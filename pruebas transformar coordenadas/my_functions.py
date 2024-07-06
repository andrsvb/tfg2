import math
import numpy as np
from pang_functions import rot


def get_rotation(vector, vector_trans):
    prod = vector[0] * vector_trans[0] + vector[1] * vector_trans[1]
    d1 = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))
    d2 = math.sqrt(math.pow(vector_trans[0], 2) + math.pow(vector_trans[1], 2))
    cos = prod / (d1 * d2)
    cross_prod = vector[0] * vector_trans[1] - vector[1] * vector_trans[0]
    sin = cross_prod / (d1 * d2)
    scale = d2 / d1
    return (sin, cos), scale


def get_trans(points, points_trans):
    num_points = points.__len__()
    if not num_points == points_trans.__len__():
        return ()
    tr_cords = np.zeros((num_points, 2))
    alpha_final, sin_final, cos_final, scale_final, dist_final = [0] * 5
    # find rotation alpha and scale
    for i in range(num_points):
        if i == num_points - 1:
            vector = [points[0, 0] - points[i, 0], points[0, 1] - points[i, 1]]
            vector_trans = [points_trans[0, 0] - points_trans[i, 0], points_trans[0, 1] - points_trans[i, 1]]
        else:
            vector = [points[i + 1, 0] - points[i, 0], points[i + 1, 1] - points[i, 1]]
            vector_trans = [points_trans[i + 1, 0] - points_trans[i, 0], points_trans[i + 1, 1] - points_trans[i, 1]]
        (sin, cos), scale = get_rotation(vector, vector_trans)
        sin_final = sin_final + sin / num_points
        cos_final = cos_final + cos / num_points
        scale_final = scale_final + scale / num_points
    alpha_final = math.atan2(sin_final, cos_final) * 180 / np.pi
    # find translation
    for i in range(num_points):
        tr_cords[i] = scale_final * points[i] @ rot(alpha_final)
        dist = points_trans[i] - tr_cords[i]
        dist_final = dist_final + dist / num_points
    return dist_final, alpha_final, scale_final
