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
    x1 = random.randint(10, 189)
    x2 = random.randint(10, 189)
    x3 = random.randint(10, 189)
    y1 = random.randint(10, 189)
    y2 = random.randint(10, 189)
    y3 = random.randint(10, 189)
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


def mutate(solution, rate):
    if random.random() < 0.5:
        # mutate points
        polygon = random.choice(solution)
        coords = [x for point in polygon[1:] for x in point]
        coords = [x +(random.randint(-10, 10) if random.random() < rate else 0) for x in coords]
        coords = [max(0, min(int(x), 200)) for x in coords]
        polygon[1:] = list(zip(coords[::2], coords[1::2]))

    else:
        # reorder polygons
        new_solution = solution[:]
        random.shuffle(new_solution)
        solution = new_solution
    return solution


def select(population):
  return [random.choice(population) for i in range(2)]


def combine(*parents):
  return [a if random.random() < 0.5 else b for a, b in zip(*parents)]

# !/usr/bin/env python

def initialise():
    SIDES = 3
    POLYGON_COUNT = 100
    return [make_polygon(SIDES) for i in range(POLYGON_COUNT)]


def run(generations=50, population_size=100, seed=31):
    # for reproducibility
    random.seed(seed)

    # initialization
    population = Population.generate(initialise, evaluate, size=10, maximize=True)
    population.evaluate
    evolution = (Evolution().survive(fraction=0.5)
                 .breed(parent_picker=select, combiner=combine)
                 .mutate(mutate_function=mutate, rate=0.1)
                 .evaluate())

    for i in range(1000):
        population = population.evolve(evolution)
        print("i =", i, " best =", population.current_best.fitness,
              " worst =", population.current_worst.fitness)
    draw(population[0].chromosome).save("solution.png")


def read_config(path):
    # read JSON or ini file, return a dictionary
    ...


if __name__ == "__main__":
    #  params = read_config(sys.argv[1])
    # run(**params)
    run()
