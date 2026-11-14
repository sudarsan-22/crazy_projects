#!/usr/bin/env python3
"""
Packages the 5 Minimo Girly parts into a native Bambu Studio project for Bambu Lab A1 Mini,
incorporating the A1 Mini 0.4 nozzle profile to eliminate the 'invalid config' prompt.
"""

import os
import zipfile
import xml.etree.ElementTree as ET

BASE_DIR = "/home/sudarsan/Documents/crazy_projects/minimo/minimo_girly"
TEMPLATE_3MF = "/home/sudarsan/Documents/crazy_projects/enclosure/enclosure_a1_mini_plate.3mf"

PARTS = [
    {
        "file": "front_shell.3mf",
        "name": "Front Shell (Pastel Pink)",
        "transform": "1 0 0 0 0 1 0 -1 0 -38.0 32.0 0.0"
    },
    {
        "file": "rear_shell.3mf",
        "name": "Rear Shell (Pastel Pink)",
        "transform": "1 0 0 0 0 -1 0 1 0 38.0 32.0 0.0"
    },
    {
        "file": "visor_frame.3mf",
        "name": "Visor Frame 1.3 inch (Piano Black)",
        "transform": "1 0 0 0 -1 0 0 0 -1 -46.0 -45.0 2.0"
    },
    {
        "file": "feet_and_paws.3mf",
        "name": "Chubby Feet Pair (Pastel Peach)",
        "transform": "1 0 0 0 1 0 0 0 1 4.0 -25.0 0.0"
    },
    {
        "file": "snap_bow.3mf",
        "name": "Snap-Fit Bow (Hot Pink)",
        "transform": "1 0 0 0 1 0 0 0 1 52.0 -45.0 6.0"
    }
]

def main():
    merged_objects = []
    
    # 1. Extract geometries from each part
    for idx, part in enumerate(PARTS, start=1):
        path = os.path.join(BASE_DIR, part["file"])
        with zipfile.ZipFile(path, 'r') as zf:
            model_data = zf.read("3D/3dmodel.model")
            root = ET.fromstring(model_data)
            ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
            for obj in root.findall('.//m:object', ns):
                obj.attrib['id'] = str(idx)
                obj.attrib['name'] = part['name']
                merged_objects.append((idx, obj, part['transform']))

    # 2. Build 3dmodel.model
    model_elem = ET.Element('{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}model', {
        'unit': 'millimeter',
        '{http://www.w3.org/XML/1998/namespace}lang': 'en-US'
    })
    
    resources = ET.SubElement(model_elem, '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}resources')
    for idx, obj, _ in merged_objects:
        resources.append(obj)

    build = ET.SubElement(model_elem, '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}build')
    for idx, _, transform in merged_objects:
        ET.SubElement(build, '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}item', {
            'objectid': str(idx),
            'transform': transform,
            'printable': '1'
        })

    model_xml = ET.tostring(model_elem, encoding='utf-8', xml_declaration=True)

    # 3. Read Bambu A1 Mini project settings from template
    bambu_files = {}
    if os.path.exists(TEMPLATE_3MF):
        with zipfile.ZipFile(TEMPLATE_3MF, 'r') as zt:
            for item in zt.namelist():
                if item.startswith("Metadata/") and not item.endswith(".model"):
                    bambu_files[item] = zt.read(item)

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="config" ContentType="text/plain"/>
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="png" ContentType="image/png"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""

    out_path = os.path.join(BASE_DIR, "bambu_a1_mini_plate.3mf")
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        zout.writestr("[Content_Types].xml", content_types)
        zout.writestr("_rels/.rels", rels)
        zout.writestr("3D/3dmodel.model", model_xml)
        for name, data in bambu_files.items():
            zout.writestr(name, data)

    print(f"Successfully packaged Bambu A1 Mini 3MF with native A1 Mini profile: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    main()
