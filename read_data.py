import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
import random

#读取原始数据
def read_origin(file, centerDim, childDim):
    with open(file, 'r') as f_obj:
        lines = f_obj.readlines()  # 逐行读取
        con_feature = []  # 所有样本的特征
        for line in lines:
            line = line.strip().split(',')  # 将字符串划分为列表
            if len(line) == (centerDim * (childDim + 1)):
                con_feature.append(line)  # 将所有样本的特征放在一个列表中中
        # 将样本的特征标准化到[0,1]中
        con_feature_array = np.array(con_feature, dtype=np.float32)  # 将列表转化为数组
        return con_feature_array




#将数据进行打乱，然后返回batch_size大小的数据
def get_batch(samples, batch_size):
    index = [i for i in range(len(samples))]
    random.shuffle(index)
    samples = samples[index]
    return samples[:batch_size]

#获取余弦相似度
def cos_similarity(g_ys,d_xs,mb_size):
    cos = 0
    samples = g_ys
    orignX = d_xs
    for j in range(mb_size):
        tem1 = samples[j]
        tem2 = orignX[j]
        cos += cosine_similarity([tem1], [tem2])  # 调用cosine_similarity函数，求归一化后的生成样本同原数据的向量余弦： 12345:0.86 123:0.85
    cos /= mb_size
    return cos
