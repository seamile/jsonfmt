import xml.etree.ElementTree as ET
from typing import Any

from utils import load_value


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
    except ET.ParseError:
        return None

    return {root.tag: element_to_dict(root)}


def dict_to_xml(dict) -> str:
    return ''
