import numpy as np
from kmeans import kmeans, findClosestCentroids, evaluate_error, init_plot


class KMeans:
    def __init__(self, draw, output, k, incremental=True):
        self.draw = draw
        self.output = output
        self.k = k
        self.incremental = incremental
        self.avg_iterations = 0
        self.avg_error = 0
        self.init_func()
        self.centroids = None

        if draw:
            init_plot()

    def init_func(self):

        def train_function(x, y, model, window_state):
            if not model:
                class Model:
                    centroids = None
                    k = self.k
                    sum_iterations = 0
                    sum_error = 0
                    i = 0
                model = Model()
            if model.centroids is not None and self.incremental:
                [centroids, index, i] = kmeans(x, model.k, model.centroids,
                                               draw=self.draw,
                                               output=self.output)
            else:
                [centroids, index, i] = kmeans(x, model.k, draw=self.draw,
                                               output=self.output)
            model.centroids = centroids
            self.centroids = centroids
            error = evaluate_error(x, centroids, index)

            if self.output:
                print "Error: ", error

            model.sum_iterations += i
            model.sum_error += error
            model.i += 1
            return model

        def predict_function(x, y, model):
            self.avg_iterations = float(model.sum_iterations) / float(model.i)
            self.avg_error = float(model.sum_error) / float(model.i)
            if self.output:
                print "Average number of iterations: ", self.avg_iterations
                print "Average error: ", self.avg_error, "\n"
            return findClosestCentroids(np.array(x).reshape(1, len(x)),
                                        model.centroids)

        self.train = train_function
        self.predict = predict_function

    def reset(self):
        self.init_func()
        if self.draw:
            init_plot()

        self.avg_iterations = 0
        self.avg_error = 0
