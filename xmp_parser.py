import fitz  # PyMuPDF
import xml.etree.ElementTree as ET
import re
import hashlib

def extract_xmp_metadata(file_path: str) -> dict:
    metadata = {
        "xmp_found": False,
        "xmp_toolkit": None,
        "create_date": None,
        "modify_date": None,
        "metadata_date": None,
        "document_id": None,
        "instance_id": None,
        "producer": None,
        "xmp_raw": None,
        "xmp_hash": None,
        "xmp_anomalies": [],
    }

    try:
        doc = fitz.open(file_path)
        xml_metadata = doc.metadata.get("xml", "")
        if not xml_metadata or "<x:xmpmeta" not in xml_metadata:
            return metadata

        metadata["xmp_found"] = True
        metadata["xmp_raw"] = xml_metadata
        metadata["xmp_hash"] = hashlib.sha256(xml_metadata.encode()).hexdigest()

        # Parse XMP
        root = ET.fromstring(xml_metadata)

        # Define namespaces (may vary slightly)
        ns = {
            'x': 'adobe:ns:meta/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'xmp': 'http://ns.adobe.com/xap/1.0/',
            'pdf': 'http://ns.adobe.com/pdf/1.3/',
            'xmpMM': 'http://ns.adobe.com/xap/1.0/mm/',
        }

        for rdf in root.findall('.//rdf:Description', ns):
            toolkit = rdf.attrib.get('{%s}Toolkit' % ns['xmp'])
            create = rdf.attrib.get('{%s}CreateDate' % ns['xmp'])
            modify = rdf.attrib.get('{%s}ModifyDate' % ns['xmp'])
            meta_date = rdf.attrib.get('{%s}MetadataDate' % ns['xmp'])
            doc_id = rdf.attrib.get('{%s}DocumentID' % ns['xmpMM'])
            inst_id = rdf.attrib.get('{%s}InstanceID' % ns['xmpMM'])
            producer = rdf.attrib.get('{%s}Producer' % ns['pdf'])

            if toolkit:
                metadata["xmp_toolkit"] = toolkit
            if create:
                metadata["create_date"] = create
            if modify:
                metadata["modify_date"] = modify
            if meta_date:
                metadata["metadata_date"] = meta_date
            if doc_id:
                metadata["document_id"] = doc_id
            if inst_id:
                metadata["instance_id"] = inst_id
            if producer:
                metadata["producer"] = producer

        # Flag anomalies
        if metadata["create_date"] == metadata["modify_date"]:
            metadata["xmp_anomalies"].append("Create and Modify date identical – potential bulk generation")
        if metadata["document_id"] and metadata["instance_id"] and metadata["document_id"] == metadata["instance_id"]:
            metadata["xmp_anomalies"].append("DocumentID equals InstanceID – possible cloning or PDF flattening")
        if metadata["xmp_toolkit"] and re.search(r"Adobe.*XMP.*Toolkit", metadata["xmp_toolkit"], re.I):
            metadata["xmp_anomalies"].append("Adobe XMP Toolkit detected – check for synthetic generation")

    except Exception as e:
        metadata["xmp_anomalies"].append(f"XMP parse failure: {str(e)}")

    return metadata