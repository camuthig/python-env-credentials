import inspect
import os


def get_base_dir():
    frame = inspect.currentframe()
    for i in range(20):
        if frame is None:
            print('Unable to find the base directory of the project')
            # WIP better error handling
            exit(1)

        file_name = os.path.basename(frame.f_code.co_filename)
        if file_name == 'manage.py':
            return os.path.abspath(os.path.dirname(file_name))

        frame = frame.f_back
