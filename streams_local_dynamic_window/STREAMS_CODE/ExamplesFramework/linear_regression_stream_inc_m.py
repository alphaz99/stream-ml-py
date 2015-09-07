if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream, _no_value
from Operators import stream_func
from Framework import Stream_Learn, LinearRegression
from Framework.LinearRegression import linear_regression

import numpy as np
import time

# Parameters

draw = True
output = False
num_features = 1
window_size = 100
num_points = 1000


def print_stream(y):
    print y

def all_func(x, y, model, state, window_state):
    if draw and model:
        linear_regression.plot(x, y, model.w)

if __name__ == "__main__":

    i = 0
    w = np.random.rand(num_features + 1, 1) * 2 - 1
    w *= 5

    m = LinearRegression.LinearRegression(draw = False, output = output, alpha = 0.001)

    x = Stream('x')

    linear_regression.init_plot()
    model = Stream_Learn(x, x, m.train, m.predict, 2, window_size, 1, num_features, all_func = all_func)
    y = model.run()

    stream_func(inputs = y, f = print_stream, f_type = 'element', num_outputs = 0)

    while i < num_points:
        z = np.random.rand(num_features + 1, 1) * 2 - 1
        # w += z / 10
        w[1] += 0.01
        # x_value = np.random.rand(1, num_features) * 2 - 1
        x_value = np.array([i]).reshape(1,1)
        x_b = np.hstack((np.ones((1,1)), x_value)).transpose()
        y_value = w.transpose().dot(x_b)[0][0]
        values = x_value.tolist()[0]
        values.append(y_value)
        x.extend([tuple(values)])
        # time.sleep(1)

        if i % 50 == 0 and i != 0:
             model.reset()

        print i
        i += 1

    print "Average error: ", m.avg_error
    print "Average errror 1:", m1.avg_error
