import os
import errno


class Utility():

    @staticmethod
    def mkdir_p(filename):
        if os.path.exists(os.path.dirname(filename)):
            return

        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as e:  # Guard against race condition
            if e.errno != errno.EEXIST:
                raise

    def abc(self):
        pass