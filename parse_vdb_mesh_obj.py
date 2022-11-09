#  pure obj parser

from lmath import box_create, box_expand_point


def parse_obj(filename, swapyz=False):
    print("parsing " + filename)

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
            v0 = int(values[1].split('/')[0]) - 1
            v1 = int(values[2].split('/')[0]) - 1
            v2 = int(values[3].split('/')[0]) - 1
            faces.append((v0, v1, v2))

    model = {
        'vertices': vertices,
        'vertex_count': len(vertices),
        'faces': faces,
        'face_count': len(faces),
        'box': box
    }

    return model