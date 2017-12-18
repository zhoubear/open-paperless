def skip_file_descriptor_check(func):
    def func_wrapper(item):
        item._skip_file_descriptor_test = True
        return func(item)
    return func_wrapper
