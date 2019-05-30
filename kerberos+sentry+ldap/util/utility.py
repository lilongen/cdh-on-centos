import os
import errno
import shutil
from ruamel.yaml import YAML


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

    @staticmethod
    def rm(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            print(e)

    @staticmethod
    def list_remove_item(l, item):
        try:
            return l.remove(item)
        except Exception as e:
            return l

    @staticmethod
    def dump_yaml_to_file(yaml_, file):
        Utility.mkdir_p(file)
        f = open(file, 'w')
        YAML().dump(yaml_, f)
        f.close()
