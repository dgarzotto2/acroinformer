import logging
from lxml import etree
from typing import Optional

logger = logging.getLogger(__name__)

def parse_xmp_toolkit(raw_xmp: bytes) -> Optional[str]:
    """
    Extracts the <xmp:Toolkit> element text from raw XMP bytes.
    """
    try:
        root = etree.fromstring(raw_xmp)
        tk = root.find(".//{http://ns.adobe.com/xap/1.0/}Toolkit")
        return tk.text if tk is not None else None
    except Exception as e:
        logger.debug("XMP parse failed", exc_info=e)
        return None