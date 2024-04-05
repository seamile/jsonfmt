import re
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from copy import deepcopy
from typing import Any, Optional, Self
from xml.dom.minidom import parseString

from .utils import safe_eval, sort_dict

RESERVED_CHARS = re.compile(r'[<>&"\']')


class Element(ET.Element):
    def __init__(self,
                 tag: str,
                 attrib={},
                 text: Optional[str] = None,
                 tail: Optional[str] = None,
                 **extra) -> None:
        super().__init__(tag, attrib, **extra)
        self.text = text
        self.tail = tail
        self.parent: Optional[Self] = None

    def __str__(self):
        def _(ele, n=0):
            indent = '    ' * n
            line = f'{indent}{ele.tag} : ATTRIB={ele.attrib}  TEXT={ele.text}\n'
            for e in ele:
                line += _(e, n + 1)  # type: ignore
            return line
        return _(self)

    @classmethod
    def makeelement(cls, tag, attrib, text=None, tail=None) -> Self:
        """Create a new element with the same type."""
        return cls(tag, attrib, text, tail)

    @classmethod
    def from_xml(cls, xml: str) -> Self:
        def clone(src: ET.Element, dst: Self):
            for child in src:
                _child = dst.spawn(child.tag, child.attrib, child.text, child.tail)
                clone(child, _child)

        root = ET.fromstring(xml.strip())
        ele = cls(root.tag, root.attrib, root.text, root.tail)
        clone(root, ele)
        return ele

    def to_xml(self,
               minimal: Optional[bool] = None,
               indent: Optional[int | str] = 2
               ) -> str:
        ele = deepcopy(self)
        for e in ele.iter():
            if len(e) > 0:
                e.text = e.text.strip() if isinstance(e.text, str) else None
            e.tail = e.tail.strip() if isinstance(e.tail, str) else None

        xml = ET.tostring(ele, 'unicode')
        if minimal or indent is None:
            return xml
        else:
            doc = parseString(xml)
            if isinstance(indent, int) or indent.isdecimal():
                indent = ' ' * int(indent)
            else:
                indent = '\t'
            return doc.toprettyxml(indent=indent)

    def spawn(self, tag: str, attrib={}, text=None, tail=None, **extra) -> Self:
        """Create and append a new child element to the current element."""
        attrib = {**attrib, **extra}
        child = self.makeelement(tag, attrib, text, tail)
        child.parent = self
        self.append(child)
        return child

    def _get_attrs(self) -> Optional[dict[str, Any]]:
        attrs = {f'@{k}': safe_eval(v) for k, v in self.attrib.items()}

        if len(self) == 0:
            if not self.text:
                return attrs or None
            else:
                value = safe_eval(self.text.strip())
                if attrs and value:
                    attrs['@text'] = value
                return attrs or value
        else:
            for n, child in enumerate(self, start=1):
                child_attrs = child._get_attrs()  # type: ignore
                if child.tag in attrs:
                    # Make a list for duplicate tags
                    previous = attrs[child.tag]
                    if n == 2:
                        attrs[child.tag] = [previous, child_attrs]
                    else:
                        previous.append(child_attrs)
                else:
                    attrs[child.tag] = child_attrs
            return attrs

    def to_py(self) -> Any:
        '''Convert into Python object'''
        attrs = self._get_attrs()
        return attrs if self.tag == 'root' else {self.tag: attrs}

    def _set_attrs(self, py_obj: Any):
        if isinstance(py_obj, Mapping):
            for key, value in py_obj.items():
                if key == '@text':
                    self.text = str(value)
                elif key[0] == '@':
                    self.set(key[1:], str(value))
                else:
                    self.spawn(key)._set_attrs(value)
        elif isinstance(py_obj, (list, tuple, set)):
            for i, item in enumerate(py_obj):
                ele = self if i == 0 else self.parent.spawn(self.tag)  # type: ignore
                if isinstance(item, Mapping):
                    ele._set_attrs(item)
                elif isinstance(item, (list, tuple, set)):
                    ele._set_attrs(str(item))
                else:
                    ele.text = str(item)
        else:
            self.text = str(py_obj)

    @classmethod
    def from_py(cls, py_obj: Any):
        if not isinstance(py_obj, dict) or len(py_obj) != 1:
            element = cls('root')
        else:
            tag, value = list(py_obj.items())[0]
            if isinstance(value, Mapping):
                element = cls(tag)
                py_obj = value
            else:
                element = cls('root')
        element._set_attrs(py_obj)
        return element


def loads(xml: str) -> Any:
    '''Load and convert an XML string into a Python object'''
    return Element.from_xml(xml).to_py()


def dumps(py_obj: Any, indent: str = 't', minimal: bool = False,
          sort_keys: bool = False) -> str:
    if sort_keys:
        py_obj = sort_dict(py_obj)
    return Element.from_py(py_obj).to_xml(indent=indent, minimal=minimal)
