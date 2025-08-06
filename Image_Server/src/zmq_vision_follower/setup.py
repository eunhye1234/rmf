from setuptools import setup

package_name = 'zmq_vision_follower'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'zmq_vision_follower = zmq_vision_follower.zmq_vision_follower:main',
        ],
    },
)
