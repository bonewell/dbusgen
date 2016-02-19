from __future__ import print_function
import os
import datetime
from header import CppWarning, CppHeader

class AbstractSaver(object):
    def save(self, path):
        '''creates directory if it is not exist and runs child's logic'''
        if not os.path.isdir(path):
            os.makedirs(path)
        self.write(path)

    def write(self, path):
        raise NotImplementedError()

class Writer(object):
    def __init__(self, filename):
        self.fd = open(filename, 'w')

    def write(self, data, end=None):
        if end is None:
            print(data, file=self.fd)
        else:
            print(data, file=self.fd, end=end)

class HeaderWriter(Writer):
    class Metadata(object):
        def __init__(self, generator, guard, includes=[], namespace=None):
            self.generator = os.path.basename(generator)
            self.guard = guard
            self.includes = includes
            self.namespace = namespace

    tpl_include = '#include %s'
    tpl_guard_begin = '#ifndef %(name)s\n#define %(name)s\n'
    tpl_guard_end = '#endif  // %(name)s'
    tpl_namespace_begin = '\nnamespace %s {'
    tpl_namespace_end = '}  // namespace %s'

    def __init__(self, filename, path='', metadata=None):
        self.metadata = metadata
        Writer.__init__(self, os.path.join(path, '%s.h' % filename))

    def __enter__(self):
        if self.metadata:
            self.write(CppWarning % self.metadata.generator)
        self.write(CppHeader % datetime.date.today().year)
        if self.metadata:
            self.write(self.tpl_guard_begin % { 'name': self.metadata.guard })
            map(lambda i: self.write(self.tpl_include % i), self.metadata.includes)
        if self.__is_namespace():
            self.write(self.tpl_namespace_begin % self.metadata.namespace)
        return self

    def __exit__(self, type, value, traceback):
        if self.__is_namespace():
            self.write(self.tpl_namespace_end % self.metadata.namespace)
        if self.metadata:
            self.write(self.tpl_guard_end % { 'name': self.metadata.guard })

    def __is_namespace(self):
         return self.metadata and self.metadata.namespace is not None

class SourceWriter(Writer):
    class Metadata(object):
        def __init__(self, generator, includes=[], namespace=None):
            self.generator = os.path.basename(generator)
            self.includes = includes
            self.namespace = namespace

    tpl_include = '#include %s'
    tpl_namespace_begin = '\nnamespace %s {'
    tpl_namespace_end = '}  // namespace %s'

    def __init__(self, filename, path='', metadata=None):
        self.metadata = metadata
        Writer.__init__(self, os.path.join(path, '%s.cc' % filename))

    def __enter__(self):
        if self.metadata:
            self.write(CppWarning % self.metadata.generator)
        self.write(CppHeader % datetime.date.today().year)
        if self.metadata:
            map(lambda i: self.write(self.tpl_include % i), self.metadata.includes)
        if self.__is_namespace():
            self.write(self.tpl_namespace_begin % self.metadata.namespace)
        return self

    def __exit__(self, type, value, traceback):
        if self.__is_namespace():
            self.write(self.tpl_namespace_end % self.metadata.namespace)

    def __is_namespace(self):
         return self.metadata and self.metadata.namespace is not None

class QmlWriter(Writer):
    class Metadata(object):
        def __init__(self, generator, parent, imports=[]):
            self.generator = os.path.basename(generator)
            self.parent = parent
            self.imports = imports

    tpl_import = 'import %s'
    tpl_parent_begin = '\n%s {'
    tpl_parent_end = '}'

    def __init__(self, filename, path='', metadata=None):
        self.metadata = metadata
        Writer.__init__(self, os.path.join(path, '%s.qml' % filename))

    def __enter__(self):
        if self.metadata:
            self.write(CppWarning % self.metadata.generator)
        self.write(CppHeader % datetime.date.today().year)
        if self.metadata:
            map(lambda i: self.write(self.tpl_import % i), self.metadata.imports)
            self.write(self.tpl_parent_begin % self.metadata.parent)
        return self

    def __exit__(self, type, value, traceback):
        self.write(self.tpl_parent_end)

class JSWriter(Writer):
    class Metadata(object):
        def __init__(self, generator):
            self.generator = os.path.basename(generator)

    pragma = '.pragma library'

    def __init__(self, filename, path='', metadata=None):
        self.metadata = metadata
        Writer.__init__(self, os.path.join(path, '%s.js' % filename))

    def __enter__(self):
        if self.metadata:
            self.write(CppWarning % self.metadata.generator)
        self.write(CppHeader % datetime.date.today().year)
        self.write(self.pragma)
        return self

    def __exit__(self, type, value, traceback):
        pass
