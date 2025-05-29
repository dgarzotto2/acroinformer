# utils/xml_utils.py

import logging
from typing import Optional
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

def parse_xmp_toolkit(raw_xmp: bytes) -> Optional[str]:
    """
    Extract the <xmp:Toolkit> element from raw XMP bytes using only the stdlib.
    """
    try:
        root = ET.fromstring(raw_xmp)
        # Namespace mapping for XMP Core
        ns = {"xmp": "http://ns.adobe.com/xap/1.0/"}
        elem = root.find(".//xmp:Toolkit", ns)
        return elem.text if elem is not None else None
    except ET.ParseError:
        logger.debug("Failed to parse XMP with ElementTree", exc_info=True)
        return None