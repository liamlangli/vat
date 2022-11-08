from math import sqrt

def vector_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def vector_normalize(a):
    l = sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    if l == 0:
        return (0, 0, 0)
    else:
        return (a[0] / l, a[1] / l, a[2] / l)

def vector_cross(a, b):
    ax = a[0]
    ay = a[1]
    az = a[2]
    bx = b[0]
    by = b[1]
    bz = b[2]

    cx = ay * bz - az * by
    cy = az * bx - ax * bz
    cz = ax * by - ay * bx

    return (cx, cy, cz)

def box_create():
    return {
        'min': [float('inf'), float('inf'), float('inf')],
        'max': [-float('inf'), -float('inf'), -float('inf')]
    }

def box_expand_point(box, a):
    box['min'][0] = min(box['min'][0], a[0])
    box['min'][1] = min(box['min'][1], a[1])
    box['min'][2] = min(box['min'][2], a[2])

    box['max'][0] = max(box['max'][0], a[0])
    box['max'][1] = max(box['max'][1], a[1])
    box['max'][2] = max(box['max'][2], a[2])

def box_expand_box(a, b):
    a['min'][0] = min(a['min'][0], b['min'][0])
    a['min'][1] = min(a['min'][1], b['min'][1])
    a['min'][2] = min(a['min'][2], a['min'][2])

    a['max'][0] = max(a['max'][0], b['max'][0])
    a['max'][1] = max(a['max'][1], b['max'][1])
    a['max'][2] = max(a['max'][2], b['max'][2])

def box_compute_size(box):
    return (box['max'][0] - box['min'][0], box['max'][1] - box['min'][1], box['max'][2] - box['min'][2])