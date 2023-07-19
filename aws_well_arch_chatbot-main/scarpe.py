from fastapi import FastAPI, UploadFile, File
import xml.etree.ElementTree as ET

app = FastAPI()

@app.post("/scrape")
async def scrape(xml_file: UploadFile = File(...)):
    print("hii")
    tree = ET.parse(xml_file.file)
    root = tree.getroot()

    # Existing code...

    # Modify the return statement to return a dictionary instead of JsonResponse
    return {
        'pattern_dict': pattern_dict,
        'Subnet_Count': count_d,
        'Full_Component_list': strip,
        'ec2_count': ec2_count,
        'single-con-list': l1,
        'front_end': front_dict,
        'comp_list': list_l1
    }
