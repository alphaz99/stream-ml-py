import numpy as np
from linear_regression import train_sgd, train, init_plot, plot, evaluate_error


class LinearRegression:
    def __init__(self, draw, output, incremental=True, alpha=0.01,
                 figsize=(15, 8)):
        self.draw = draw
        self.output = output
        self.avg_error = 0
        self.incremental = incremental
        self.init_func()
        self.w = 0
        self.alpha = alpha

        if draw:
            init_plot(figsize)

    def init_func(self):

        if self.incremental:
            def train_function(x, y, model, window_state):

                step_size = window_state[3]
                current_window_size = window_state[0]
                max_window_size = window_state[4]

                if not model:
                    class Model:
                        w = np.zeros((x.shape[1] + 1, 1))
                        sum_error = 0
                        i = 0
                        if x.shape[1] == 1:
                            x_sum = 0
                            y_sum = 0
                            xy_sum = 0
                            xx_sum = 0
                    model = Model()

                    if x.shape[1] == 1:
                        model.x_sum = np.sum(x)
                        model.y_sum = np.sum(y)
                        model.xy_sum = np.sum(x * y)
                        model.xx_sum = np.sum(x ** 2)

                elif x.shape[1] == 1:
                    for i in range(-step_size, 0):
                        x_value = x[i].tolist()[0]
                        y_value = y[i].tolist()[0]
                        model.x_sum += x_value
                        model.y_sum += y_value
                        model.xy_sum += x_value * y_value
                        model.xx_sum += x_value ** 2

                if x.shape[1] == 1:

                    n = x.shape[0]
                    model.w[1] = (model.xy_sum - model.x_sum * model.y_sum /
                                  float(n)) / (model.xx_sum - model.x_sum *
                                               model.x_sum / float(n))
                    model.w[0] = (model.y_sum/float(n) - model.w[1] *
                                  model.x_sum/float(n))

                    self.w = model.w

                    if self.draw:
                        plot(x, y, model.w)

                    if (max_window_size - current_window_size < step_size and
                            not window_state[1]):
                        for i in range(0, step_size - (max_window_size -
                                                       current_window_size)):
                            x_value = x[i].tolist()[0]
                            y_value = y[i].tolist()[0]
                            model.x_sum -= x_value
                            model.y_sum -= y_value
                            model.xy_sum -= x_value * y_value
                            model.xx_sum -= x_value ** 2

                    if window_state[1]:

                        for i in range(0, step_size):
                            x_value = x[i].tolist()[0]
                            y_value = y[i].tolist()[0]
                            model.x_sum -= x_value
                            model.y_sum -= y_value
                            model.xy_sum -= x_value * y_value
                            model.xx_sum -= x_value ** 2

                else:
                    model.w = train_sgd(x, y, self.alpha, model.w, self.draw)
                    self.w = model.w
                error = evaluate_error(x, y, model.w)
                if self.output:
                    print "Error: ", error

                model.sum_error += error
                model.i += 1
                return model

        else:
            def train_function(x, y, model, window_state):
                if not model:
                    class Model:
                        w = np.zeros((x.shape[1] + 1, 1))
                        sum_error = 0
                        i = 0
                    model = Model()

                model.w = train(x, y, self.draw)
                self.w = model.w
                error = evaluate_error(x, y, model.w)
                if self.output:
                    print "Error: ", error

                model.sum_error += error
                model.i += 1
                return model

        def predict_function(x, y, model):
            self.avg_error = float(model.sum_error) / float(model.i)
            if self.output:
                print "Average error: ", self.avg_error, "\n"

            X_array = np.array(x).reshape(1, len(x))
            y_array = np.array(y).reshape(1, len(y))
            return evaluate_error(X_array, y_array, model.w) ** 0.5

        self.train = train_function
        self.predict = predict_function

    def reset(self):
        self.init_func()
        if self.draw:
            init_plot()
        self.avg_error = 0
