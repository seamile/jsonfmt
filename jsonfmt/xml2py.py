import sys
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from copy import deepcopy
from xml.dom.minidom import parseString

from .utils import safe_eval, sort_dict

if sys.version_info < (3, 11):
    from typing import Any, Dict, Optional, TypeVar, Union
    Self = TypeVar('Self', bound='XmlElement')
else:
    from typing import Any, Dict, Optional, Self, Union


class _list(list):
    pass


class XmlElement(ET.Element):
    def __init__(self,
                 tag: str,
                 attrib: Optional[dict] = None,
                 text: Optional[str] = None,
                 tail: Optional[str] = None,
                 **extra) -> None:
        attrib = attrib or {}
        super().__init__(tag, attrib, **extra)
        self.text = text
        self.tail = tail
        self.parent: Optional[Self] = None

    @classmethod
    def makeelement(cls, tag, attrib, text=None, tail=None) -> Self:
        """Create a new element with the same type."""
        return cls(tag, attrib, text, tail)

    @classmethod
    def clone(cls, src: Union[Self, ET.Element], dst: Optional[Self] = None) -> Self:
        if dst is None:
            dst = cls(src.tag, src.attrib, src.text, src.tail)

        for child in src:
            _child = dst.spawn(child.tag, child.attrib, child.text, child.tail)
            cls.clone(child, _child)

        return dst

    @classmethod
    def from_xml(cls, xml: str) -> Self:
        root = ET.fromstring(xml.strip())
        return cls.clone(root)

    def to_xml(self,
               minimal: Optional[bool] = None,
               indent: Optional[Union[int, str]] = 2
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

    def spawn(self, tag: str,
              attrib: Optional[dict] = None,
              text: Optional[str] = None,
              tail: Optional[str] = None,
              **extra) -> Self:
        """Create and append a new child element to the current element."""
        attrib = attrib or {}
        attrib = {**attrib, **extra}
        child = self.makeelement(tag, attrib, text, tail)
        child.parent = self
        self.append(child)
        return child

    def _get_attrs(self) -> Optional[Dict[str, Any]]:
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
            if self.text:
                value = safe_eval(self.text.strip())
                if value:
                    attrs['@text'] = value

            _tags = []  # tags of type "_list"
            for child in self:
                child_attrs = child._get_attrs()  # type: ignore
                if child.tag in attrs:
                    # Make a list for duplicate tags
                    previous = attrs[child.tag]
                    if not isinstance(previous, _list):
                        attrs[child.tag] = _list([previous, child_attrs])
                        _tags.append(child.tag)
                    else:
                        previous.append(child_attrs)
                else:
                    attrs[child.tag] = child_attrs

            # recover "_list" to "list"
            for k in _tags:
                attrs[k] = list(attrs[k])

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
                elif isinstance(value, list):
                    for v in value:
                        self.spawn(key)._set_attrs(v)
                else:
                    self.spawn(key)._set_attrs(value)
        elif isinstance(py_obj, (list, tuple, set)):
            if self.parent is None:
                return self.spawn(self.tag)._set_attrs(py_obj)
            else:
                for i, item in enumerate(py_obj):
                    if len(self.parent) > i:
                        ele = self.parent[i]
                    else:
                        ele = self.parent.spawn(self.tag)

                    if isinstance(item, (list, tuple, set)):
                        ele.text = str(item)
                    else:
                        ele._set_attrs(item)  # type: ignore
        else:
            self.text = str(py_obj)

    @classmethod
    def from_py(cls, py_obj: Any):
        if not isinstance(py_obj, dict) or len(py_obj) != 1:
            root = cls('root')
        else:
            tag, value = list(py_obj.items())[0]
            if isinstance(value, Mapping):
                root = cls(tag)
                py_obj = value
            else:
                root = cls('root')
        root._set_attrs(py_obj)
        return root


def loads(xml: str) -> Any:
    '''Load and convert an XML string into a Python object'''
    return XmlElement.from_xml(xml).to_py()


def dumps(py_obj: Any, indent: str = 't', minimal: bool = False,
          sort_keys: bool = False) -> str:
    if sort_keys:
        py_obj = sort_dict(py_obj)
    return XmlElement.from_py(py_obj).to_xml(indent=indent, minimal=minimal)
