from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent


setup(
    install_requires=(HERE / "requirements.txt").read_text(), 
    use_scm_version=True,
)