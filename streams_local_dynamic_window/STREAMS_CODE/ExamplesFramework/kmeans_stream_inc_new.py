if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from Stream import Stream, _no_value
from Operators import stream_func
from Framework import Stream_Learn
from Framework import KMeans
from Framework.KMeans import kmeans

import numpy as np

# Parameters

draw = True
output = True
num_centroids = 5
k = 5
window_size = 1000
num_points = 15000


if __name__ == "__main__":

    i = 0

    centroids = kmeans.initialize(num_centroids)

    m = KMeans.KMeans(draw = draw, output = output, k = k)

    x = Stream('x')

    model = Stream_Learn(x, x, m.train, m.predict, k, window_size, 1, 2)
    y = model.run()

    while i < num_points:
        index = np.random.randint(0, num_centroids)
        z = np.random.rand(1,2) * 2 - 1
        centroids[index] = centroids[index].reshape(1,2) +  z * 2
        x.extend([tuple(kmeans.initializeDataCenter(centroids[index], 1, 1).tolist()[0])])
        print i
        i += 1

        if i % 200 == 0:
            model.reset()

    print "Average number of iterations: ", m.avg_iterations
    print "Average error: ", m.avg_error