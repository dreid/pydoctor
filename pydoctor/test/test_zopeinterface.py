from pydoctor.zopeinterface import ZopeInterfaceSystem
from pydoctor.test.test_astbuilder import fromText
from pydoctor.test.test_packages import processPackage

import py

# we set up the same situation using both implements and
# classImplements and run the same tests.

def test_implements():
    src = '''
    import zope.interface

    class IFoo(zope.interface.Interface):
        pass
    class IBar(zope.interface.Interface):
        pass

    class Foo:
        zope.interface.implements(IFoo)
    class FooBar(Foo):
        zope.interface.implements(IBar)
    class OnlyBar(Foo):
        zope.interface.implementsOnly(IBar)
    '''
    implements_test(src)

def test_classImplements():
    src = '''
    import zope.interface
    class IFoo(zope.interface.Interface):
        pass
    class IBar(zope.interface.Interface):
        pass
    class Foo:
        pass
    class FooBar(Foo):
        pass
    class OnlyBar(Foo):
        pass
    zope.interface.classImplements(Foo, IFoo)
    zope.interface.classImplements(FooBar, IBar)
    zope.interface.classImplementsOnly(OnlyBar, IBar)
    '''
    implements_test(src)

def test_implementer():
    src = '''
    import zope.interface

    class IFoo(zope.interface.Interface):
        pass
    class IBar(zope.interface.Interface):
        pass

    @zope.interface.implementer(IFoo)
    class Foo:
        pass
    @zope.interface.implementer(IBar)
    class FooBar(Foo):
        pass
    class OnlyBar(Foo):
        zope.interface.implementsOnly(IBar)
    '''
    implements_test(src)


def implements_test(src):
    mod = fromText(src, 'zi', systemcls=ZopeInterfaceSystem)
    ifoo = mod.contents['IFoo']
    ibar = mod.contents['IBar']
    foo = mod.contents['Foo']
    foobar = mod.contents['FooBar']
    onlybar = mod.contents['OnlyBar']

    assert ifoo.isinterface and ibar.isinterface
    assert not foo.isinterface and not foobar.isinterface and not foobar.isinterface

    assert not foo.implementsOnly and not foobar.implementsOnly
    assert onlybar.implementsOnly

    assert foo.implements_directly == ['zi.IFoo']
    assert foo.allImplementedInterfaces == ['zi.IFoo']
    assert foobar.implements_directly == ['zi.IBar']
    assert foobar.allImplementedInterfaces == ['zi.IBar', 'zi.IFoo']
    assert onlybar.implements_directly == ['zi.IBar']
    assert onlybar.allImplementedInterfaces == ['zi.IBar']

    assert ifoo.implementedby_directly == ['zi.Foo']
    assert ifoo.allImplementations == ['zi.Foo', 'zi.FooBar']
    assert ibar.implementedby_directly == ['zi.FooBar', 'zi.OnlyBar']
    assert ibar.allImplementations == ['zi.FooBar', 'zi.OnlyBar']


def test_subclass_with_same_name():
    src = '''
    class A:
        pass
    class A(A):
        pass
    '''
    fromText(src, 'zi', systemcls=ZopeInterfaceSystem)

def test_multiply_inheriting_interfaces():
    src = '''
    from zope.interface import Interface, implements

    class IOne(Interface): pass
    class ITwo(Interface): pass
    class One: implements(IOne)
    class Two: implements(ITwo)
    class Both(One, Two): pass
    '''
    mod = fromText(src, 'zi', systemcls=ZopeInterfaceSystem)
    assert len(mod.contents['Both'].allImplementedInterfaces) == 2

def test_attribute():
    src = '''
    import zope.interface as zi
    class C:
        attr = zi.Attribute("docstring")
    '''
    mod = fromText(src, systemcls=ZopeInterfaceSystem)
    assert len(mod.contents['C'].contents) == 1

def test_interfaceclass():
    system = processPackage('interfaceclass', systemcls=ZopeInterfaceSystem)
    mod = system.allobjects['interfaceclass.mod']
    assert mod.contents['AnInterface'].isinterface

def test_warnerproofing():
    src = '''
    from zope import interface
    Interface = interface.Interface
    class IMyInterface(Interface):
        pass
    '''
    mod = fromText(src, systemcls=ZopeInterfaceSystem)
    assert mod.contents['IMyInterface'].isinterface

def test_zopeschema():
    src = '''
    from zope import schema, interface
    class IMyInterface(interface.Interface):
        text = schema.TextLine(description="fun in a bun")
    '''
    mod = fromText(src, systemcls=ZopeInterfaceSystem)
    text = mod.contents['IMyInterface'].contents['text']
    assert text.docstring == 'fun in a bun'
    assert text.kind == "TextLine"

def test_with_underscore():
    src = '''
    from zope import schema, interface
    class IMyInterface(interface.Interface):
        attribute = interface.Attribute(_("fun in a bun"))
        text = schema.TextLine(description=_("fun in a bap"))
    '''
    mod = fromText(src, systemcls=ZopeInterfaceSystem)
    text = mod.contents['IMyInterface'].contents['attribute']
    assert text.docstring == 'fun in a bun'
    assert text.kind == "Attribute"

    text = mod.contents['IMyInterface'].contents['text']
    assert text.docstring == 'fun in a bap'
    assert text.kind == "TextLine"

def test_zopeschema_inheritance():
    src = '''
    from zope import schema, interface
    from zope.schema import Int as INTEGERSCHMEMAFIELD
    class MyTextLine(schema.TextLine):
        pass
    class MyOtherTextLine(MyTextLine):
        pass
    class IMyInterface(interface.Interface):
        mytext = MyTextLine(description="fun in a bun")
        myothertext = MyOtherTextLine(description="fun in another bun")
        myint = INTEGERSCHMEMAFIELD(description="not as much fun")
    '''
    mod = fromText(src, systemcls=ZopeInterfaceSystem)
    mytext = mod.contents['IMyInterface'].contents['mytext']
    assert mytext.docstring == 'fun in a bun'
    assert mytext.kind == "MyTextLine"
    myothertext = mod.contents['IMyInterface'].contents['myothertext']
    assert myothertext.docstring == 'fun in another bun'
    assert myothertext.kind == "MyOtherTextLine"
    myint = mod.contents['IMyInterface'].contents['myint']
    assert myint.kind == "Int"
