from distutils.core import setup
import py2exe

setup(windows=["decrypter.py"], options={
    "py2exe": {
        "bundle_files": 1,
        "compressed": 1,
        "optimize": 1
        }
    }, zipfile = None)
