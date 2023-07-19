import json
import uvicorn
import xml.etree.ElementTree as ET
from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/scrape")
async def scrape(xml_file: UploadFile = File(...)):
    print("hii")
    tree = ET.parse(xml_file.file)
    root = tree.getroot()

    ### COUNT OF PRIVATE AND PUBLIC SUBNETS
    l = []
    for mxCell in root.iter("mxCell"):
        if "value" in mxCell.attrib:
            value = mxCell.attrib["value"]
            if value != "":
                l.append(value)
    pub_s = 0
    pri_s = 0
    sub_net = 0

    for i in range(len(l)):
        if l[i] == 'Public subnet':
            pub_s += 1
            sub_net += 1
        elif l[i] == 'Private subnet':
            pri_s += 1
            sub_net += 1
        else:
            continue

    count_d = {}
    count_d['Private subnet'] = pri_s
    count_d['Public subnet'] = pub_s
    count_d['Subnet count'] = sub_net

    ###### CODE FOR COUNT OF SUBNETS ENDS HERE

    ####CODE FOR COMPONENT FLOW STARTS HERE
    source_target_dict = {}
    for cell in root.iter('mxCell'):
        source = cell.get('source')
        target = cell.get('target')
        source_target_dict[cell.get('id')] = {'source': source, 'target': target}

    clean_dict = {k: v for k, v in source_target_dict.items() if v['source'] is not None or v['target'] is not None}
    print(clean_dict)

    result = {}
    listed = []
    for key, value in clean_dict.items():
        listed.append(value)
    print(listed)

    id_shape_dict = {}
    for mxCell in root.iter("mxCell"):
        if "style" in mxCell.attrib:
            style = mxCell.attrib["style"]
            style_pairs = style.split(";")
            shape = None
            for pair in style_pairs:
                if "=" in pair:
                    key, value = pair.split("=")
                    if key == "shape":
                        shape = value
                        break
            if shape is not None:
                id = mxCell.attrib["id"]
                id_shape_dict[id] = shape

    key_id = []
    value_id = []
    for k, v in id_shape_dict.items():
        key_id.append(k)
        value_id.append(v)

    stripped_list = [s.split('.', 1)[1] for s in value_id]
    strip = [s.split('.', 1)[1] for s in stripped_list]
    print(strip)
    dict1 = dict(zip(key_id, strip))
    print(dict1)
    print(listed)
    for d in listed:
        d['source'] = dict1[d['source']]
        d['target'] = dict1[d['target']]

    ###CODE FOR COMPONENT FLOW ENDS HERE

    ##### CODE TO EXTRACT THE NAME OF COMPONENTS
    shapes = root.findall(".//mxCell[@vertex='1']")
    style_dict = {}
    for shape in shapes:
        style = shape.attrib['style']
        style_list = style.split(';')
        style_dict[shape.attrib['id']] = {}
        for style_item in style_list:
            if '=' in style_item:
                key, value = style_item.split('=')
                style_dict[shape.attrib['id']][key] = value

    data = style_dict.copy()
    shapes = []
    for key, value in data.items():
        for k, val in value.items():
            if k == 'shape':
                shapes.append(val)

    stripped_list = [s.split('.', 1)[1] for s in shapes]
    strip = [s.split('.', 1)[1] for s in stripped_list]
    print(strip)
    s = {i for i in strip}
    lis = list(s)
    print(lis)
    if 'group' in lis:
        index = lis.index('group')
        lis[index] = 'subnet'
    if 'productIcon' in lis:
        index2 = lis.index('productIcon')
        lis[index2] = 's3'
    for i in strip:
        if 'group' in lis:
            index = lis.index('group')
            lis[index] = 'subnet'

    ######CODE END FOR LIST OF COMPONENTS IN THE LIST lis

    data_list = []
    for item in listed:
        source = item['source']
        target = item['target']
        data_list.append(source)
        data_list.append(target)
    print(data_list)

    pattern_dict = {}

    for i in range(len(data_list) - 3):
        item1 = data_list[i]
        item2 = data_list[i + 1]
        item3 = data_list[i + 2]
        item4 = data_list[i + 3]

        if item2 == item3 and item1 == item4:
            if item2 not in pattern_dict:
                pattern_dict[item2] = {}

            if item1 not in pattern_dict[item2]:
                pattern_dict[item2][item1] = 0

            pattern_dict[item2][item1] += 2

    print(pattern_dict)

    ec2_count = strip.count('ec2')

    keys = list(pattern_dict.keys())
    keys.append('route_table')
    keys.append('internet_gateway')

    l1 = [item for item in data_list if item not in keys]

    vpc_list = ['subnet', 'internet_gateway', 'route_table']
    rem_list = ['subnet', 'internet_gateway', 'route_table', 'rds']
    list_l1 = [element for element in lis if element not in rem_list]
    front_dict = {'vpc': vpc_list}

    Json_data = {
        'pattern_dict': pattern_dict,
        'Subnet_Count': count_d,
        'Full_Component_list': strip,
        'ec2_count': ec2_count,
        'single-con-list': l1,
        'front_end': front_dict,
        'comp_list': list_l1
    }

    return Json_data
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)