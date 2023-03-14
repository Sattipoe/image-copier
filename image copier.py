#!/usr/bin/env python

import sys
import random
import random
from PIL import Image, ImageDraw, ImageChops
from evol import Evolution, Population


def draw(solution):
    image = Image.new("RGB", (200, 200))
    canvas = ImageDraw.Draw(image, "RGBA")
    for polygon in solution:
        canvas.polygon(polygon[1:], fill=polygon[0])
    return image


def make_polygon(SIDES):
    # 0 <= R|G|B < 256, 30 <= A <= 60, 10 <= x|y < 190
    # made random number generator for each of the points
    R = random.randint(0, 255)
    G = random.randint(0, 255)
    B = random.randint(0, 255)
    A = random.randint(30, 60)
    x1 = random.randint(10, 190)
    x2 = random.randint(10, 190)
    x3 = random.randint(10, 190)
    y1 = random.randint(10, 190)
    y2 = random.randint(10, 190)
    y3 = random.randint(10, 190)
    return [(R, G, B, A), (x1, y1), (x2, y2), (x3, y3)]


MAX = 255 * 200 * 200
TARGET = Image.open("darwin.png")
TARGET.load()  # read image and close the file


def evaluate(solution):
    image = draw(solution)
    diff = ImageChops.difference(image, TARGET)
    hist = diff.convert("L").histogram()
    count = sum(i * n for i, n in enumerate(hist))
    return (MAX - count) / MAX


def mutate(solution, rate, add_rate=1, delete_rate=0.1, shift_rate=0.1, shuffle_rate=0.1):
    r = random.random()
    if r < add_rate:
        # add a new polygon
        solution.append(make_polygon(3))
    elif r < add_rate + delete_rate and len(solution) > 1:
        # delete a random polygon
        del solution[random.randint(0, len(solution) - 1)]
    elif r < add_rate + delete_rate + shift_rate:
        #random points of the polygon
        polygon = random.choice(solution)
        for i in range(1, len(polygon)):
            if random.random() < rate:
                x, y = polygon[i]
                x += random.randint(-10, 10)
                y += random.randint(-10, 10)
                x = max(10, min(x, 190))
                y = max(10, min(y, 190))
                polygon[i] = (x, y)
    elif r < add_rate + delete_rate + shift_rate + shuffle_rate:
        # shuffle the order of polygons
        random.shuffle(solution)
    elif r < add_rate + delete_rate + shift_rate + shuffle_rate + 0.25:
        polygon = random.choice(solution)
        coords = [x for point in polygon[1:] for x in point]
        coords = [x + (random.randint(-10, 10) if random.random() < rate else 0) for x in coords]
        coords = [max(0, min(int(x), 200)) for x in coords]
        polygon[1:] = list(zip(coords[::2], coords[1::2]))
    else:
        polygon = random.choice(solution)
        R = max(0, min(polygon[0][0] + random.randint(-30, 30), 255))
        G = max(0, min(polygon[0][1] + random.randint(-30, 30), 255))
        B = max(0, min(polygon[0][2] + random.randint(-30, 30), 255))
        A = max(0, min(polygon[0][3] + random.randint(-10, 10), 60))
        polygon[0] = (R, G, B, A)

    return solution

def select(population):
    # tournament size of 5
    tournament_size = 5

    # select two parents based on their fitness values
    parents = []
    for i in range(2):
        tournament = random.sample(population, tournament_size)
        winner = max(tournament, key=lambda x: x.fitness)
        parents.append(winner)

    return parents


def combine(*parents):
    return [a if random.random() < 0.5 else b for a, b in zip(*parents)]


# !/usr/bin/env python

def initialise():
    SIDES = 3
    POLYGON_COUNT = 100
    return [make_polygon(SIDES) for i in range(POLYGON_COUNT)]


def run(generations=500, population_size=100, seed=31):
    # for reproducibility
    random.seed(seed)

    # initialization
    population = Population.generate(initialise, evaluate, size=population_size, maximize=True)
    population.evaluate()
    evolution = (Evolution().survive(fraction=0.5)
                 .breed(parent_picker=select, combiner=combine)
                 .mutate(mutate_function=mutate, rate=0.1)
                 .evaluate())

    best_solution = None
    best_fitness = float("-inf")

    for i in range(generations):
        population = population.evolve(evolution)
        print("i =", i, " best =", population.current_best.fitness,
              " worst =", population.current_worst.fitness)
        if population.current_best.fitness > best_fitness:
            best_solution = population.current_best
            best_fitness = population.current_best.fitness

    return best_solution


def read_config(path):
    # read JSON or ini file, return a dictionary
    ...


if __name__ == "__main__":
    #  params = read_config(sys.argv[1])
    # run(**params)
    run()
