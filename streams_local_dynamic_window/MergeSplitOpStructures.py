def merge_structure(h, f, in_streams, window_size, step_size, state=None):
    def g(windows, state=None):
        return [f(windows)] if state is None else [f(windows, state)]
    return h(g, in_streams, 1, window_size, step_size, state=None)[0]


def split_structure(h, f, in_stream, num_out_streams,
                    window_size, step_size, state=None):
    def g(windows, state=None):
        return f(windows[0]) if state is None else f(windows[0], state)
    return h(g, [in_stream], num_out_streams,
                               window_size, step_size, state=None)


def op_structure(h, f, in_stream, window_size, step_size, state=None):
    def g(windows, state=None):
        return [f(windows[0])] if state is None else [f(windows[0], state)]
    return h(g, [in_stream], 1, window_size,
                               step_size, state=None)[0]
