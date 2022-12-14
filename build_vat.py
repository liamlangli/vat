#!/usr/local/bin/python3

import json
from math import ceil, log2
from os import listdir
from os.path import getmtime, isfile, join

import imageio
import numpy as np
from lmath import (box_compute_size, box_create, box_expand_box, vector_add,
                   vector_cross, vector_normalize)
from parse_vdb_mesh_obj import parse_obj


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

def save_exr(filename, data):
    imageio.imwrite(filename, data.astype(np.float32))

def save_png(filename, data):
    imageio.imwrite(filename, data.astype(np.uint8))

def save_meta(filename, box, width, height):
    with open(filename, 'w') as f:
        meta = {
            'width': width,
            'height': height,
            'box': box
        }
        json.dump(meta, f)

def main(data_path, output_path="./output/"):
    files = [join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f)) and f.endswith('.obj')]
    files.sort(key = lambda x: getmtime(x))

    models = []
    max_vertex_count = 0
    box = box_create()
    for file in files:
        model = parse_obj(file)
        calculate_normal(model)
        models.append(model)
        max_vertex_count = max(model['face_count'] * 3, max_vertex_count)
        box_expand_box(box, model['box'])
    
    model_count = len(models)
    print("max vertex count " + str(max_vertex_count))
    print("frame count " + str(model_count))

    width = 1 << (ceil(log2(max_vertex_count)))
    height = 1 << (ceil(log2(model_count)))
    print("create output texture [{}, {}]".format(width, height))

    vertex_tex = np.zeros((height, width, 3))
    normal_tex = np.zeros((height, width, 4))

    box_min = box['min']
    box_size = box_compute_size(box)
    inv_delta_x = 1.0 / box_size[0]
    inv_delta_y = 1.0 / box_size[1]
    inv_delta_z = 1.0 / box_size[2]

    print("normalizing animation data")
    for y in range(height):
        if y >= model_count:
            break

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

            vertex_tex[y][i * 3][0] = (v0[0] - box_min[0]) * inv_delta_x
            vertex_tex[y][i * 3][1] = (v0[1] - box_min[1]) * inv_delta_y
            vertex_tex[y][i * 3][2] = (v0[2] - box_min[2]) * inv_delta_z

            vertex_tex[y][i * 3 + 1][0] = (v1[0] - box_min[0]) * inv_delta_x
            vertex_tex[y][i * 3 + 1][1] = (v1[1] - box_min[1]) * inv_delta_y
            vertex_tex[y][i * 3 + 1][2] = (v1[2] - box_min[2]) * inv_delta_z

            vertex_tex[y][i * 3 + 2][0] = (v2[0] - box_min[0]) * inv_delta_x
            vertex_tex[y][i * 3 + 2][1] = (v2[1] - box_min[1]) * inv_delta_y
            vertex_tex[y][i * 3 + 2][2] = (v2[2] - box_min[2]) * inv_delta_z

            normal_tex[y][i * 3][0] = n0[0] * 255
            normal_tex[y][i * 3][1] = n0[1] * 255
            normal_tex[y][i * 3][2] = n0[2] * 255
            normal_tex[y][i * 3][3] = 255

            normal_tex[y][i * 3 + 1][0] = n1[0] * 255
            normal_tex[y][i * 3 + 1][1] = n1[1] * 255
            normal_tex[y][i * 3 + 1][2] = n1[2] * 255
            normal_tex[y][i * 3 + 1][3] = 255

            normal_tex[y][i * 3 + 2][0] = n2[0] * 255
            normal_tex[y][i * 3 + 2][1] = n2[1] * 255
            normal_tex[y][i * 3 + 2][2] = n2[2] * 255
            normal_tex[y][i * 3 + 2][3] = 255

    print("save output file")
    save_exr(join(output_path, 'vat_vertex_tex.exr'), vertex_tex)
    save_png(join(output_path, 'vat_normal_tex.png'), normal_tex)
    save_meta(join(output_path, 'meta.json'), box, max_vertex_count, model_count)

if __name__ == '__main__':
    main('../export/')