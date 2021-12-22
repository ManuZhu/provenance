import re
import os


def walkFile(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if re.search('dot', file):
                extract_KV(path + "/" + file, path + "/relation.txt", path + "/attribute.txt")


def extract_KV(path, res_path, nodeAttributePath):
    num = 1
    KV_dict = {}
    nodeMap = {}
    res_list = []
    attributeMapList = []
    indexCount = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            indexCount += 1
            line = line.strip('\n')
            matchObj = re.match(r'"(.*)" -> "(.*)" \[label="(.*)" color="(\w*)".*', line)
            if matchObj:
                if matchObj.group(1) not in KV_dict:
                    KV_dict[matchObj.group(1)] = num
                    attributeMapList.append(str(num) + " " + nodeMap[matchObj.group(1)])
                    num += 1
                parent = KV_dict[matchObj.group(1)]
                if matchObj.group(2) not in KV_dict:
                    KV_dict[matchObj.group(2)] = num
                    attributeMapList.append(str(num) + " " + nodeMap[matchObj.group(2)])
                    num += 1
                child = KV_dict[matchObj.group(2)]
                res_list.append(str(child) + "  " + str(parent))
            else:
                if indexCount >= 5 and line != "}":
                    nodeStr = line[1:33]
                    attribute = line[35:]
                    attrinum = 0
                    for i in attribute:
                        if i == "=":
                            attrinum += 1
                    nodeMap[nodeStr] = str(attrinum)
        f.close()

    print(res_list)
    with open(res_path, "w") as fw:
        res = "\n".join(res_list)
        fw.write(res)
        fw.close()
    with open(nodeAttributePath, "w", encoding="UTF-8") as saveFile:
        attributeMap = "\n".join(attributeMapList)
        saveFile.write(attributeMap)
        saveFile.close()
