#!/usr/bin/env python

from os.path import join

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('sandbox',parent_package,top_path)

    sandbox_packages = []
    try:
        sandbox_file = open(join(config.package_path,
                                 'enabled_packages.txt'), 'rU')
    except IOError:
        pass
    else:
        for line in sandbox_file:
            p = line.strip()
            if not p or p.startswith('#'):
                continue
            sandbox_packages.append(p)
        sandbox_file.close()

    for p in sandbox_packages:
        config.add_subpackage(p)

    # All subpackages should be commented out in the version
    # committed to the repository. This prevents build problems
    # for people who are not actively working with these
    # potentially unstable packages.

    # You can put a list of modules you want to always enable in the
    # file 'enabled_packages.txt' in this directory (you'll have to create it).
    # Since this isn't under version control, it's less likely you'll
    # check it in and screw other people up :-)

    # An example package:
    #config.add_subpackage('exmplpackage')

    # Monte Carlo package
    #config.add_subpackage('montecarlo')

    # Robert Kern's corner:
    #config.add_subpackage('rkern')

    # ODRPACK
    #config.add_subpackage('odr')

    # Delaunay triangulation and Natural Neighbor interpolation
    #config.add_subpackage('delaunay')

    # elementwise numerical expressions
    #config.add_subpackage('numexpr')

    # Adaptation of Scientific.IO (2.4.9) to use NumPy
    #config.add_subpackage('netcdf')

    # Finite Difference Formulae package
    #config.add_subpackage('fdfpack')

    # Package with useful constants and unit-conversions defined
    #config.add_subpackage('constants')

    # Interpolating between sparse samples
    #config.add_subpackage('buildgrid')

    # David Cournapeau's corner: autocorrelation, lpc, lpc residual
    #config.add_subpackage('cdavid')

    # New spline package (based on scipy.interpolate)
    #config.add_subpackage('spline')

    # Radial basis functions package
    #config.add_subpackage('rbf')

    # pyloess
    config.add_subpackage('pyloess')


    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
