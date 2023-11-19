from collections import deque
from fractions import Fraction
import sys


center = Fraction(1, 2)

faces = [
    (0, center, center),
    # (1, center, center),
    (center, 0, center),
    (center, 1, center),
    (center, center, 0),
    # (center, center, 1),

    # (1, center, center),
    (2, center, center),
    (1 + center, 0, center),
    (1 + center, 1, center),
    (1 + center, center, 0),
    (1 + center, center, 1),

    (0, center, 1 + center),
    (1, center, 1 + center),
    (center, 0, 1 + center),
    (center, 1, 1 + center),
    # (center, center, 1),
    (center, center, 2),
]

origin = (center, center, center)
centers = [
    (center, center, center),
    (1 + center, center, center),
    (center, center, 1 + center),
]


pieces = [
    'RROOOOOOOOOROB',
    'OYOOBOROOOOORR',
    'RROOYOOOOOOOYB',
    'YYOOROROOOOOOB',
    'OOOORROROYORYY',
    'OYOOOYOOOOOOOB',
    'ROOOYOOYOOOYBO',
    'ORYOYOYYOROROR',
    'OOOOYYOYOROYRO',
]

dices = [
    [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
    [[1, 0, 0], [0, 0, 0], [0, 0, 1]],
    [[0, 0, 1], [0, 0, 0], [1, 0, 0]],
    [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    [[0, 0, 1], [0, 1, 0], [1, 0, 0]],
    [[1, 0, 1], [0, 0, 0], [1, 0, 1]],
    [[1, 0, 1], [0, 1, 0], [1, 0, 1]],
    [[1, 1, 1], [0, 0, 0], [1, 1, 1]],
    [[1, 0, 1], [1, 0, 1], [1, 0, 1]],
]

id_matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
x_matrix = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
y_matrix = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
z_matrix = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
rot_matrices = [x_matrix, y_matrix, z_matrix]


def vecadd(x, y):
    return [a + b for a, b in zip(x, y)]


def vecsub(x, y):
    return [a - b for a, b in zip(x, y)]


def matmul(x, y):
    z = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                z[i][j] += x[i][k] * y[k][j]
    return z


def matvec(x, y):
    z = [0, 0, 0]
    for i in range(3):
        for k in range(3):
            z[i] += x[i][k] * y[k]
    return z


def gen_group():
    q = deque()
    s = set()
    rotations = []
    q.append(id_matrix)
    s.add(str(id_matrix))
    while q:
        x = q.popleft()
        rotations.append(x)
        for r in rot_matrices:
            y = matmul(x, r)
            if str(y) not in s:
                q.append(y)
                s.add(str(y))
    return rotations


def apply_rotation(center, rotation):
    return vecadd(matvec(rotation, vecsub(center, origin)), origin)


def is_bad(x):
    return x <= 0 or x >= 3


def to_int(arr):
    return [int(elem) for elem in arr]


def get_ix(taken, ix):
    i = ix[0]
    j = ix[1]
    k = ix[2]
    return taken[i][j][k]


def set_ix(taken, ix, val):
    i = ix[0]
    j = ix[1]
    k = ix[2]
    taken[i][j][k] = val


def on_side(val):
    return val == 0 or val == 3


def sum_3d(x):
    y = [[sum(b) for b in a] for a in x]
    z = [sum(a) for a in y]
    return sum(z)


def check_distinct(dot_counts):
    for i, elem in enumerate(sorted(dot_counts)):
        if elem != i + 1:
            return False
    return True


def match_grids(dice, grid, target_color):
    for i in range(3):
        for j in range(3):
            if dice[i][j] == 0:
                if grid[i][j] != 'O' and grid[i][j] is not None:
                    return False
            else:
                if grid[i][j] != target_color and grid[i][j] is not None:
                    return False
    return True


def check_intermediate(colors, target_color, debug=False):
    grids = [[3 * [None] for _ in range(3)] for _ in range(6)]
    for k, v in colors.items():
        coords = []
        for i, elem in enumerate(k):
            if elem.denominator == 1:
                face = 2 * i + (1 if elem > 0 else 0)
            else:
                coords.append(int(elem))
        grids[face][coords[0]][coords[1]] = v

    for grid in grids:
        if debug:
            for row in grid:
                for elem in row:
                    print("-" if elem is None else elem, end="")
                print()
            print()

        has_match = False
        for dice in dices:
            if match_grids(dice, grid, target_color):
                has_match = True
                break

        if not has_match:
            return False

    return True


def check_solution(colors, target_color):
    s = [0 for _ in range(6)]
    t = [[] for _ in range(6)]
    for k, v in colors.items():
        if v == target_color:
            if k[0] == 0:
                s[0] += 1
                t[0].append((k[1], k[2]))
            elif k[0] == 3:
                s[1] += 1
                t[1].append((k[1], k[2]))
            elif k[1] == 0:
                s[2] += 1
                t[2].append((k[0], k[2]))
            elif k[1] == 3:
                s[3] += 1
                t[3].append((k[0], k[2]))
            elif k[2] == 0:
                s[4] += 1
                t[4].append((k[0], k[1]))
            elif k[2] == 3:
                s[5] += 1
                t[5].append((k[0], k[1]))

    if not check_distinct(s):
        return False

    return True


def translate_centers(centers, taken, i, j, k):
    new_centers = []

    for center in centers:
        nc = [i + center[0], j + center[1], k + center[2]]
        if any(map(is_bad, nc)):
            return False

        nc = [int(x) for x in nc]
        if get_ix(taken, nc) != 0:
            return False

        new_centers.append(nc)

    return new_centers


def bkt(rotations, rotated_centers, taken, colors, solution, target_color, level):
    for k, v in colors.items():
        if v != target_color and v != 'O' and v is not None:
            if any(map(on_side, k)):
                return
        if v == target_color:
            if not any(map(on_side, k)):
                return

    if not check_intermediate(colors, target_color):
        return

    if level >= 1:
        num_occupied = sum_3d(taken)
        if 3 * level != num_occupied:
            print(f"Expected {3 * level} squares to be occupied, found {num_occupied}")
            sys.exit()

    if level == 9:
        if check_solution(colors, target_color):
            print("Solution found:")
            for elem in solution:
                print("\t", elem)
            sys.exit()

        return

    for x in [level]:
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    if taken[i][j][k] == 0:
                        for ir, (rot, cs) in enumerate(zip(rotations, rotated_centers)):
                            new_centers = translate_centers(cs, taken, i, j, k)
                            if new_centers:
                                for ix in new_centers:
                                    set_ix(taken, ix, 1)

                                face_centers = []
                                for face_idx, face in enumerate(faces):
                                    fmc = apply_rotation(face, rot)
                                    fmt = (i + fmc[0], j + fmc[1], k + fmc[2])
                                    colors[fmt] = pieces[x][face_idx]
                                    face_centers.append(fmt)

                                solution.append((pieces[x], (i, j, k), ir, new_centers))
                                bkt(rotations, rotated_centers, taken, colors, solution, target_color, level + 1)
                                solution.pop()

                                for fmt in face_centers:
                                    colors[fmt] = None

                                for ix in new_centers:
                                    set_ix(taken, ix, 0)


def main():
    rotations = gen_group()
    rotated_centers = []
    for rotation in rotations:
        cs = [apply_rotation(center, rotation) for center in centers]
        rotated_centers.append(cs)

    taken = [
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
    ]
    colors = {}
    target_color = 'Y'
    pieces.sort(key=lambda x: -x.count(target_color))
    bkt(rotations, rotated_centers, taken, colors, [], target_color, 0)


if __name__ == '__main__':
    main()
