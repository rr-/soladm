from setuptools import setup, find_packages

setup(
    author='Marcin Kurczewski',
    author_email='rr-@sakuya.pl',
    name='soladm',
    long_description='Soldat Admin client',
    version='0.1',
    url='https://github.com/rr-/soladm',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'soladm = soladm.__main__:main'
        ]
    },

    install_requires=[
        'urwid',
        'urwid_readline',
    ],
    package_dir={'soladm': 'soladm'},
    package_data={'soladm': ['data/*.*']},

    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Games/Entertainment',
        'Topic :: Utilities',
    ])
