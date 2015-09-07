import numpy as np
import matplotlib.pyplot as plt
import random


def initialize(k):
    centroids = (np.random.rand(k, 2) * 2 - 1) * 5
    return centroids


def initializeCentroids(X, k):
    index = random.sample(xrange(0, len(X)), k)
    return X[index, :]


def findClosestCentroids(X, centroids):
    index = np.array([np.argmin([np.dot(x_i - y_k, x_i - y_k)
                                 for y_k in centroids])
                      for x_i in X])
    return index


def computeCentroids(X, index, k):
    centroids = np.zeros((k, 2))

    for i in range(0, k):
        idx = np.where(index == i)[0]
        if len(idx) != 0:
            data = X[idx, :]
            centroids[i, :] = np.mean(data, 0)

    return centroids


def kmeans(X, k, initial_centroids=None, draw=False, output=False):
    num_iters = 0
    if initial_centroids is not None:
        centroids = initial_centroids
    else:
        centroids = initializeCentroids(X, k)

    previous = centroids
    index = np.zeros((len(X), 1))
    previous_index = np.zeros((len(X), 1))

    while True:
        index = findClosestCentroids(X, centroids)
        if np.array_equal(index, previous_index):
            break

        if num_iters != 0 and output:
            print np.count_nonzero(index - previous_index),\
                " data points changed color"
        previous_index = index
        if draw:
            plotKMeans(X, centroids, previous, index, k)

        previous = centroids
        centroids = computeCentroids(X, index, k)

        num_iters += 1

    if output:
        print "Num iters: ", num_iters
    return [centroids, index, num_iters]


def initializeDataCenter(centroid, scale, n):
    X = np.random.normal(centroid, scale=scale, size=(n, 2))
    return X


def initializeData(n, k, scale):
    centroids = initialize(k)

    for i in range(0, len(centroids)):
        if i == 0:
            X = initializeDataCenter(centroids[i], scale, n)
        else:
            X = np.vstack((X, initializeDataCenter(centroids[i], scale, n)))

    return X


def plotData(X, index, k):
    rainbow = plt.get_cmap('rainbow')
    plt.scatter(X[:, 0], X[:, 1], c=index, cmap=rainbow)


def plotKMeans(X, centroids, previous, index, k):
    plt.clf()
    plotData(X, index, k)
    plt.scatter(centroids[:, 0], centroids[:, 1], 20)

    for i in range(0, k):
        plt.plot((centroids[i, 0], previous[i, 0]), (centroids[i, 1],
                 previous[i, 1]), color='black')
    plt.draw()


def init_plot():
    plt.ion()
    f = plt.figure(figsize=(15, 8))
    plt.show()


def evaluate_error(X, centroids, index):
    s = 0
    for i in range(0, len(X)):
        centroid_index = index[i]
        s += np.dot(X[i] - centroids[centroid_index], X[i] -
                    centroids[centroid_index])

    return float(s) / X.shape[0]
