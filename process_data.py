import os

# 原来为6 5
# flash   imagetragick   phishingEmail
# samba  tomcat  webmin  wordpress
dataSetName = "flash"
dataSetKind = "pass"
center_dim = 6
child_dim = 5

#将溯源图序列化为溯源向量

def walk_passFolder(path,res_path):#处理PASS数据集
    for root, dirs, files in os.walk(path):# root 表示当前正在访问的文件夹路径; dirs 表示该文件夹下的子目录名list; files 表示该文件夹下的文件list
        #print(files)
        for dir in dirs:
            path2 = path + "/"+dir+"/"+"2.txt"
            print(path2)
            with open(path2) as f:
                lines = f.readlines()
                vectorization(lines,res_path)

def walk_spadeFile(path,res_path):#处理SPADE数据集
    for root, dirs, files in os.walk(path):
        for file in files:
            path2 = path + "/" + file
            with open(path2) as f:
                lines = f.readlines()
                vectorization(lines,res_path)

def vectorization(lines,res_path):
    node_dict = {} #存放 parent ： childs
    node_important_dict = {} #存放 parent 对应的重要度，即child的个数

    #将溯源度的节点重要度信息保存在字典中
    for line in lines:
        line = line.strip('\n')
        temp_line = line.split()
        if len(temp_line) != 2:
            continue
        parent = temp_line[0]
        child = temp_line[1]
        if parent in node_dict:
            temp_list = node_dict[parent]
            if child not in temp_list:
                temp_list.append(child)
                node_important_dict[parent] += 1
                node_dict[parent] = temp_list
        else:
            temp_list=[child]
            node_dict[parent] = temp_list
            node_important_dict[parent] = 1

    #将node_improtant_dict 按照节点的重要度 逆序排列
    node_important_sort = sorted(node_important_dict.items(),key=lambda item:item[1],reverse=True)
    center_nodes = []
    for item in node_important_sort:
        center_nodes.append(item[0])
        if len(center_nodes) == center_dim:
            break

    if len(center_nodes) < center_dim:
        return

    center_nodes_temp = []
    if dataSetKind == "pass":
        center_nodes = [float(x) for x in center_nodes]  #这一步需要注意，SPADE数据集为int(),PASS数据集为float()
    elif dataSetKind == "spade":
        center_nodes = [int(x) for x in center_nodes]
    center_nodes = sorted(center_nodes)
    for node in center_nodes:
        # if node > 10:
        #     center_nodes_temp.append(node)
        center_nodes_temp.append(node)

    center_nodes = [str(x) for x in center_nodes_temp]
    # center_nodes = [str(x) for x in center_nodes]
    if len(center_nodes ) < center_dim:
        return

    #构造中心节点的邻域，其中邻域同样根据节点重要度来进行排序
    center_node_dict = {}
    for center_node in center_nodes:
        temp_list = []
        if center_node in node_dict:
            temp_list = node_dict[center_node]
        if len(temp_list) < child_dim:
            return
        temp_dict = {}
        for node in temp_list:
            if node in node_important_dict:
                temp_dict[node] = node_important_dict[node]
            else:
                temp_dict[node] = 0
        child_sort = sorted(temp_dict.items(), key=lambda item:item[1],reverse=True)
        temp_list2 = []
        for item in child_sort:
            temp_list2.append(item[0])
            if len(temp_list2) == child_dim:
                break
        center_node_dict[center_node] = temp_list2

    #将向量化后的溯源图写入文本
    vector_list = []
    for key, value in center_node_dict.items():
        vector_list.append(key)
        vector_list.extend(value)
    print(len(vector_list))
    with open(res_path,"a+") as f:
        res = ",".join(vector_list)
        f.write(res+'\n')

def main():
    # walk_passFolder("D:/graduate/dataset/PASS_flash","D:/graduate/dataset/PASS_flash.txt")#对已经处理好的PASS数据集进行向量化处理
    # walk_spadeFile("../dataset/wordpress_process", "../dataset/wordpress_final.txt")#对已经处理的SPADE数据集进行向量化处理
    # walk_passFolder("../dataset/txtGFile", "../dataset/final/BSD_Final_"+str(center_dim)+"_"+str(child_dim)+".txt")  # 对已经处理好的PASS数据集进行向量化处理
    # walk_passFolder("../dataset/flash", "../dataset/final/flash_final.txt")
    dataSetPath = "data/" + dataSetName
    finalTxtPath = "data/final/" + dataSetName + "/" + dataSetName + "Final_"+ str(center_dim) + "_" + str(child_dim) + ".txt"
    if dataSetKind == "pass":
        walk_passFolder(dataSetPath, finalTxtPath)
    elif dataSetKind == "spade":
        walk_spadeFile(dataSetPath, finalTxtPath)
