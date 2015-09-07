import numpy as np
import matplotlib.pyplot as plt
import math


# Stochastic gradient descent - linear regression
def train_sgd(X, y, alpha, w, draw=False):
    X_b = np.hstack((np.ones((X.shape[0], 1)), X))

    previous_error = -1
    error = -1

    stop = False
    num_iters = 0

    while not stop:
        for i in range(0, len(X)):
            w = w - alpha / len(X) * (np.dot(np.transpose(w),
                                      X_b[i].reshape(X_b.shape[1], 1)) -
                                      y[i]) * X_b[i].reshape(X_b.shape[1], 1)

            error = evaluate_error(X, y, w)
            if previous_error == -1:
                previous_error = error
            elif (math.fabs(error - previous_error) < 0.01 * previous_error and
                  num_iters > 10000):
                stop = True
                break

            previous_error = error
            num_iters += 1

    if draw:
        plot(X, y, w)

    return w


# Matrix linear regression
def train(X, y, draw=False):

    # Add bias term
    X_b = np.hstack((np.ones((X.shape[0], 1)), X))

    # Compute pseudo-inverse
    X_inverse = (np.linalg.inv(np.transpose(X_b).dot(X_b)).dot(
                 np.transpose(X_b)))

    # Compute w
    w = X_inverse.dot(y)

    if draw:
        plot(X, y, w)

    return w


# Plot data
def plot(X, y, w):

    X_b = np.hstack((np.ones((X.shape[0], 1)), X))

    y_predict = X_b.dot(w)

    plt.clf()
    plt.plot(X[:, 0], y_predict, 'r-', X[:, 0], y, 'o')
    plt.draw()


def init_plot(figsize=(15, 8)):
    plt.ion()
    f = plt.figure(figsize=figsize)
    plt.show()


# Get error
def evaluate_error(X, y, w):
    X_b = np.hstack((np.ones((X.shape[0], 1)), X))

    y_predict = X_b.dot(w)

    dist = (y - y_predict) ** 2

    return float(np.sum(dist)) / X.shape[0]


def predict(X, w):
    X_b = np.hstack((np.ones((X.shape[0], 1)), X))
    return X_b.dot(w)
