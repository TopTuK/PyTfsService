from setuptools import setup

setup(name='tfsservice',
      version='0.1',
      description='Library to work with TFS workitems',
      url='https://github.com/TopTuK/PyTfsService',
      author='TopTuK',
      author_email='cydoor88@gmail.com',
      license='MIT',
      packages=['tfsservice'],
      install_requires=[
          'TFSAPI',
      ],
      zip_safe=False)