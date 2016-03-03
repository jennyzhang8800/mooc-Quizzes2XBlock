"""Setup for quizzes2 XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='quizzes2-xblock',
    version='0.1',
    description='quizzes2 XBlock',   # TODO: write a better description.
    packages=[
        'quizzes2',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'quizzes2 = quizzes2:Quizzes2XBlock',
        ]
    },
    package_data=package_data("quizzes2", ["static", "public"]),
)
