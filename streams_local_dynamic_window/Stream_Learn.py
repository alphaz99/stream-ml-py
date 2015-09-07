import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from functools import partial
from Stream import Stream, _no_value
from Agent import *
from Operators import stream_func

import numpy as np


def stream_learn(data_train, data_out, train_func, predict_func, window_size, step_size, num_features):
    """Generates an output stream for learning on data.

    This function takes an input data source `data_train` and produces an output stream
    with values corresponding to learning on the data source. This data source can either
    be a `Stream` of data or a batch dataset which may be a `numpy` array. In the `Stream` case, 
    learning is done on windows of `data_train`. In the batch case learning is done once.
    The output stream is generated by predicting on `data_out`, a `Stream` of data.

    Parameters
    ----------
    data_train : `Stream` or numpy.ndarray or other
        A `Stream` object or an `numpy` array containing data to be trained on. In the case of
        `Stream`, the `Stream` object contains tuples of values where each tuple represents a row
        of data. Each tuple must have at least `num_features` values. In the case of an array,
        the array must have at least `num_features` columns. Any additional values / columns
        correspond to the output y data. If this is not a Stream or `numpy` array, the data will
        not be split into x and y.
    data_out : `Stream`
        A `Stream` object containing data to generate predictions on. The `Stream` contains tuples
        of values where each tuple represents a row of data and must have at least `num_features`
        values.
    train_func : function
        A function that takes as input 2 `numpy` arrays of data and a model object and returns a model object.
        The first `numpy` array 'x' will have dimensions either `window_size` x `num_features` or N x `num_features`
        for `Stream` learning and batch learning respectively, where N refers to the total number of
        training examples. The second `numpy` array 'y' will have dimensions `window_size` x num_outputs or
        N x num_outputs for `Stream` training and batch training respectively, where num_outputs refers to
        the number of y outputs for an input. For example, num_outputs = 1 refers to 1 scalar output.
        For unsupervised learning, num_outputs = 0.
        The model object returned by this function is used in `predict_func` to generate a prediction
        for an input.
    predict_func : function
        A function that takes as input 2 tuples corresponding to 1 row of data and a model and returns
        a prediction. This function takes as input the same model type as returned by `train_func`. The first
        tuple 'x' has `num_features` values and the second tuple 'y' has num_output values, where num_outputs
        refers to the number of y outputs for an input.
    window_size : int
        An int specifying the size of the window to train on. A `numpy` array with `window_size` rows
        will be passed to train_func if `data_train` is a `Stream`. This will be ignored for batch learning.
    step_size : int
        An int specifying the number of tuples to move the window by for `Stream` learning. This will be
        ignored for batch learning.
    num_features : int
        An integer that describes the number of features in the data.

    Returns
    -------
    y_predict : `Stream`
        A `Stream` object containing the predictions outputted by `predict_func`.

    Examples
    --------
    This example illustrates how to do linear regression on a stream of 2-tuples using scikit-learn as
    **supervised learning**.

    >>> from sklearn import linear_model
    >>> def train_function(x, y, model):
    >>>     regr = linear_model.LinearRegression()
    >>>     regr.fit(x, y)
    >>>     return regr
    >>>
    >>> def predict_function(x, y, model):
    >>>     y_predict = model.predict(x)
    >>>     return y_predict.flatten().tolist()[0]
    >>>
    >>> data_train = Stream('data_train')
    >>> data_out = Stream('data_out')
    >>> y = stream_learn(data_train, data_out, train_function, predict_function, 5, 1, 1)
    >>> y.set_name('y')
    >>> data_train.extend([(0,0), (1,2), (2,4), (3,6), (4,8)])
    >>> y.print_recent()
    y = []
    >>> data_out.extend([6, 7, 8])
    >>> y.print_recent()
    y = [12.000000000000004, 14.000000000000004, 16.000000000000004]


    This example illustrates how to do linear regression on a batch of data with 2 features using scikit-learn
    as **supervised learning**.

    >>> from sklearn import linear_model
    >>> def train_function(x, y, model):
    >>>     regr = linear_model.LinearRegression()
    >>>     regr.fit(x, y)
    >>>     return regr
    >>>
    >>> def predict_function(x, y, model):
    >>>     y_predict = model.predict(x)
    >>>     return y_predict.flatten().tolist()[0]
    >>>
    >>> data_train = np.array([(0,0), (1,2), (2,4), (3,6), (4,8)])
    >>> data_out = Stream('data_out')
    >>> y = stream_learn(data_train, data_out, train_function, predict_function, 5, 1, 1)
    >>> y.set_name('y')
    >>> y.print_recent()
    y = []
    >>> data_out.extend([6, 7, 8])
    >>> y.print_recent()
    y = [12.000000000000004, 14.000000000000004, 16.000000000000004]

    
    This example illustrates how to do novelty detection on a stream of 2-tuples using scikit-learn as
    **unsupervised learning**.

    >>> from sklearn import svm
    >>> def train_function(x, y, model):
    >>>     model = svm.OneClassSVM()
    >>>     model.fit(x)
    >>>     return model
    >>>
    >>> def predict_function(x, y, model):
    >>>     y_predict = model.predict(x)
    >>>     return y_predict.flatten().tolist()[0]
    >>>
    >>> data_train = Stream('data_train')
    >>> y = stream_learn(data_train, data_train, train_function, predict_function, 6, 1, 2)
    >>> y.set_name('y')
    >>> data_train.extend([(0,0), (1,1), (1,-1), (-1,1), (-1,-1)])
    >>> y.print_recent()
    y = []
    >>> data_train.extend([(0.5,0.5)])
    >>> y.print_recent()
    y = [1.0]
    >>> data_train.extend([(1.5,2)])
    >>> y.print_recent()
    y = [1.0, -1.0]    

    """


    trained = [False]
    model = [None]

    def split_training_test(x_y):
        x, y = x_y
        if np.random.uniform() >= 0.6:
            return [_no_value, _no_value, x, y]
        else:
            return [x, y, _no_value, _no_value]

    stream_split = partial(stream_func, f_type='element', f=split_training_test, num_outputs=4)


    def train(lst):
        data = np.array(lst)
        x = data[:, 0:num_features]
        y = data[:, num_features:]
        model[0] = train_func(x, y, model[0])
        trained[0] = True
        # return model

    stream_train = partial(stream_func, f_type='window', f=train, num_outputs=0, window_size=window_size, step_size=step_size)

    def predict(n):
        if trained[0]:
            if not isinstance(n, list):
                return predict_func(n, None, model[0])
            
            x = n[0:num_features]
            y = n[num_features:]
            return predict_func(x, y, model[0])
        return _no_value


    stream_predict = partial(stream_func, f_type='element', f=predict, num_outputs=1)
    
    # x_train, y_train, x_test, y_test = stream_split([x, y])

    if isinstance(data_train, Stream):
        # model_stream = stream_train(data_train)
        stream_train(data_train)
    elif isinstance(data_train, np.ndarray):
        x = data_train[:, 0:num_features]
        y = data_train[:, num_features:]
        train_func(x, y, None)
        trained[0] = True
    else:
        train_func(data_train, None, None)
        trained[0] = True

    y_predict = stream_predict(data_out)

    return y_predict



