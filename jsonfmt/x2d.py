import xml.etree.ElementTree as ET
from typing import Any

from .utils import load_value, print_err


def element_to_dict(element: ET.Element) -> Any:
    result: dict = {f'@{k}': load_value(v) for k, v in element.attrib.items()}

    if len(element) == 0:
        value = load_value(element.text.strip()) if element.text else ''
        if result and value:
            result.update({'@text': value})

        return result if result else value

    for child in element:
        child_dict = element_to_dict(child)
        if child.tag in result:
            previous = result[child.tag]
            if isinstance(previous, list):
                previous.append(child_dict)
            else:
                result[child.tag] = [previous, child_dict]
        else:
            result[child.tag] = child_dict

    return result


def xml_to_dict(xml_text: str) -> dict[str, Any] | None:
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError as err:
        print_err(err)

    return {root.tag: element_to_dict(root)}


def _dict_to_xml(dictionary, parent):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            child = ET.SubElement(parent, key)
            _dict_to_xml(value, child)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    child = ET.SubElement(parent, key)
                    _dict_to_xml(item, child)
                else:
                    child = ET.SubElement(parent, key)
                    child.text = str(item)
        else:
            child = ET.SubElement(parent, key)
            child.text = str(value)


def dict_to_xml(dictionary, root_tag='root') -> Any:
    root = ET.Element(root_tag)
    _dict_to_xml(dictionary, root)
    return ET.tostring(root, encoding='utf-8').decode('utf-8')
