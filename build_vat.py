#!/usr/local/bin/python3

from math import sqrt
from os import listdir
from os.path import isfile, join

from lmath import vector_add, vector_cross, vector_normalize, box_create, box_expand_box, box_compute_size

import numpy as np
import png
from parse_vdb_mesh_obj import parse_obj

def main(data_path, output_path="./output/"):
    files = [f for f in listdir(data_path) if isfile(join(data_path, f))]
    files.sort()

    models = []
    max_vertex_count = 0
    box = box_create()
    for file in files:
        filename = join(data_path, file)
        model = parse_obj(filename)
        calculate_normal(model)
        models.append(model)
        max_vertex_count = max(model['face_count'] * 3, max_vertex_count)
        box_expand_box(box, model['box'])
    
    # model_count is frame_count
    model_count = len(models)
    vertex_tex = np.zeros((max_vertex_count, model_count, 4))
    normal_tex = np.zeros((max_vertex_count, model_count, 4))

    box_min = box['min']
    box_size = box_compute_size(box)
    inv_delta_x = 65535.0 / box_size[0]
    inv_delta_y = 65535.0 / box_size[1]
    inv_delta_z = 65535.0 / box_size[2]

    for y in range(model_count):
        model = models[y]
        vertices = model['vertices']
        normals = model['normals']
        faces = model['faces']
        for i, f in enumerate(faces):
            v0 = vertices[f[0]]
            v1 = vertices[f[1]]
            v2 = vertices[f[2]]

            n0 = normals[f[0]]
            n1 = normals[f[1]]
            n2 = normals[f[2]]

            vertex_tex[i * 3][y][0] = (v0[0] - box_min[0]) * inv_delta_x
            vertex_tex[i * 3][y][1] = (v0[1] - box_min[1]) * inv_delta_y
            vertex_tex[i * 3][y][2] = (v0[2] - box_min[2]) * inv_delta_z
            vertex_tex[i * 3][y][3] = 65535

            vertex_tex[i * 3 + 1][y][0] = (v1[0] - box_min[0]) * inv_delta_x
            vertex_tex[i * 3 + 1][y][1] = (v1[1] - box_min[1]) * inv_delta_y
            vertex_tex[i * 3 + 1][y][2] = (v1[2] - box_min[2]) * inv_delta_z
            vertex_tex[i * 3 + 1][y][3] = 65535

            vertex_tex[i * 3 + 2][y][0] = (v2[0] - box_min[0]) * inv_delta_x
            vertex_tex[i * 3 + 2][y][1] = (v2[1] - box_min[1]) * inv_delta_y
            vertex_tex[i * 3 + 2][y][2] = (v2[2] - box_min[2]) * inv_delta_z
            vertex_tex[i * 3 + 2][y][3] = 65535

            normal_tex[i * 3][y][0] = n0[0] * 255
            normal_tex[i * 3][y][1] = n0[1] * 255
            normal_tex[i * 3][y][2] = n0[2] * 255
            normal_tex[i * 3][y][3] = 255

            normal_tex[i * 3 + 1][y][0] = n1[0] * 255
            normal_tex[i * 3 + 1][y][1] = n1[1] * 255
            normal_tex[i * 3 + 1][y][2] = n1[2] * 255
            normal_tex[i * 3 + 1][y][3] = 255

            normal_tex[i * 3 + 2][y][0] = n2[0] * 255
            normal_tex[i * 3 + 2][y][1] = n2[1] * 255
            normal_tex[i * 3 + 2][y][2] = n2[2] * 255
            normal_tex[i * 3 + 2][y][3] = 255
    save_png(join(output_path, 'vertex_tex.png'), vertex_tex, 16)
    save_png(join(output_path, 'normal_tex.png'), normal_tex, 8)

def save_png(filename, data, bitdepth = 16):
    with open(filename, 'wb') as f:
        writer = png.Writer(width=data.shape[1], height=data.shape[0], bitdepth=bitdepth)
        data_list = data.reshape(-1, data.shape[1] * data.shape[2]).tolist()
        writer.write(f, data_list)

def calculate_normal(model):
    vertices = model['vertices']
    normals = []

    for _ in vertices:
        n = (0.0, 0.0, 0.0)
        normals.append(n)

    for f in model['faces']:
        i0 = f[0]
        i1 = f[1]
        i2 = f[2]

        v0 = vertices[i0]
        v1 = vertices[i1]
        v2 = vertices[i2]

        n = triangle_cross_vector(v0, v1, v2)
        normals[i0] = vector_add(normals[i0], n)
        normals[i1] = vector_add(normals[i1], n)
        normals[i2] = vector_add(normals[i2], n)

    for i, n in enumerate(normals):
        normals[i] = vector_normalize(n)

    model['normals'] = normals

def triangle_cross_vector(v0, v1, v2):
    ax = v1[0] - v0[0]
    ay = v1[1] - v0[1]
    az = v1[2] - v0[2]

    bx = v2[0] - v0[0]
    by = v2[1] - v0[1]
    bz = v2[2] - v0[2]

    return vector_cross((ax, ay, az), (bx, by, bz))

if __name__ == '__main__':
    main('../cache_fluid_4b85f272/mesh')