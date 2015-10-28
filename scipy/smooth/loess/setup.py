#!/usr/bin/env python
__author__ = "Pierre GF Gerard-Marchant ($Author$)"
__version__ = '1.0'
__revision__ = "$Revision$"
__date__     = '$Date$'

from os.path import join


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info, dict_append
    config = Configuration('loess', parent_package, top_path)

    # Configuration of LOESS
    f_sources = ('loessf.f', 'linpack_lite.f')
    config.add_library('floess',
                       sources=[join('src', x) for x in f_sources])
    blas_info = get_info('blas_opt')
    build_info = {}
    dict_append(build_info, **blas_info)
    dict_append(build_info, libraries=['floess'])
    sources = ['_loess.pyx',
               'loess.c', 'loessc.c', 'misc.c', 'predict.c']
    headers = ['S.h', 'cloess.h', 'loess.h',
               'c_loess.pxd']
    config.add_extension('_loess',
                         sources=[join('src', x) for x in sources],
                         depends=[join('src', x) for x in headers],
                         **build_info)
    config.add_data_dir('tests')
    return config

if __name__ == "__main__":
    from numpy.distutils.core import setup
    config = configuration(top_path='').todict()
    setup(**config)
