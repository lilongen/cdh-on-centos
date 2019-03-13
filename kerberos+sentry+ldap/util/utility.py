import os
import errno


class Utility():

    @staticmethod
    def mkdir_p(file_name):
        dir_name = os.path.dirname(file_name)
        if dir_name == '' or os.path.exists(dir_name) :
            return

        try:
            os.makedirs(dir_name)
        except OSError as e:  # Guard against race condition
            if e.errno != errno.EEXIST:
                raise

    def abc(self):
        pass
