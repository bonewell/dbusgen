class Interface(object):
    """
        Has atributes:
        - string name
    """
    pass

class EnumerationElement(object):
    """
        Has atributes:
            - name string
            - int value
            - string internal name
    """
    pass

class Enumeration(object):
    """
        Has atributes:
            - string name
            - EnumerationElement list elements
            - Interface interface
    """
    pass

class Structure(object):
    """
        Has atributes:
            - string name
            - Interface interface
    """
    pass

class Function(object):
    """
        Has atributes:
            - string name
            - string provider
            - string type
            - Interface interface
    """
    pass

class Parameter(object):
    """
        Has atributes:
            - string name
            - string type
            - bool mandatory
            - int minlength
            - int maxlength
            - int minsize
            - int maxsize
            - bool is_array
            - string minvalue
            - string maxvalue
            - string defvalue
            - object parent (Structure or Function)
    """
    pass
