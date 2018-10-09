from setuptools import setup

setup(name='eedlab',
      version='0.1',
      description='My lab setup',
      url='http://github.com/othane/eedlab',
      author='Oliver Thane',
      author_email='othane@gmail.com',
      license='MIT',
      packages=['eedlab'],
      install_requires=[
          'python-vxi11>=0.9',
          'python-usbtmc==0.8',
          'pyusb==1.0.2',
          'universal-usbtmc==0.3.5',
      ],
      zip_safe=False)
