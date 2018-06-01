from setuptools import setup, find_packages

setup(
    name='ffmpeg_cmd_gen',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    version="0.1",
    description="Ffmpeg command generator",
    author='Shashi',
    author_email='',
    url='',
    keywords=['ffmpeg', 'command', 'generator'],
    include_package_data=True,
    entry_points={'console_scripts': ['pyinstrument = pyinstrument.__main__:main',
                                      'ffmpeg_cmd_gen=ffmpeg_cmd_gen.ffmpeg_cmd_gen:main']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Testing',
     ]
)
