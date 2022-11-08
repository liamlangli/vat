#  pure obj parser

from lmath import box_create, box_expand_point

def parse_obj(filename, swapyz=True):
    vertices = []
    faces = []

    box = box_create()

    for line in open(filename, "r"):
        if line.startswith('#'): continue

        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = list(map(float, values[1:4]))
            if swapyz:
                v = v[0], v[2], v[1]
            box_expand_point(box, v)
            vertices.append(v)
        elif values[0] == 'f':
            faces.append((int(values[1]) - 1, int(values[2]) - 1, int(values[3]) - 1))

    model = {
        'vertices': vertices,
        'vertex_count': len(vertices),
        'faces': faces,
        'face_count': len(faces),
        'box': box
    }

    return model