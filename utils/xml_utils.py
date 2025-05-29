# utils/xml_utils.py

import logging
from typing import Optional
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def parse_xmp_toolkit(raw_xmp) -> Optional[str]:
    """
    Extract the <xmp:Toolkit> element from raw XMP metadata.
    Accepts:
      - bytes (raw XML)
      - str (XML text)
      - A PyPDF2 XMP object (with .xml or .rdf attribute)
    Returns the toolkit string, or None if not found / parse fails.
    """
    try:
        # 1) Normalize to bytes
        if isinstance(raw_xmp, bytes):
            xml_bytes = raw_xmp

        elif isinstance(raw_xmp, str):
            xml_bytes = raw_xmp.encode("utf-8")

        else:
            # PyPDF2 XMPMeta / XmpInformation object
            xml_str = None
            # Try common attributes
            for attr in ("xml", "rdf", "raw_xml"):
                if hasattr(raw_xmp, attr):
                    xml_str = getattr(raw_xmp, attr)
                    break

            if xml_str is None:
                return None

            xml_bytes = xml_str.encode("utf-8") if isinstance(xml_str, str) else xml_str

        # 2) Parse with stdlib ElementTree
        root = ET.fromstring(xml_bytes)

        # 3) Look for xmp:Toolkit in the XMP namespace
        ns = {"xmp": "http://ns.adobe.com/xap/1.0/"}
        elem = root.find(".//xmp:Toolkit", ns)
        return elem.text if elem is not None else None

    except Exception:
        logger.debug("XMP Toolkit parsing failed", exc_info=True)
        return None