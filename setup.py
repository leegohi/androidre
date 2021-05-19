from setuptools import (
    find_packages,
    setup,
)
def install_requires():
    return ["fire"]
setup(
    name='droidbox',
    url="""https://github.com/leegohi/androidre
        """,
    version="1.0",
    description='A android reverse tools for spider.',
    entry_points={
        'console_scripts': [
            'droidbox = androidre.droidbox:main',
        ],
    },
    author='walle',
    author_email='walle88@qq.com',
    packages=find_packages(),
    install_requires=install_requires(),
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: Beta',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Intended Audience :: Spider',
    ],
)