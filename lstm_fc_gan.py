import logging
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from read_data import read_origin,get_batch,cos_similarity
from mod_core_rnn_cell_impl import LSTMCell
import time
import matplotlib.pyplot as plt
import os

'''log = logging.getLogger('tensorflow')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('my.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)'''

# 设置numpy超参数
np.set_printoptions(suppress=True, precision=16)

datasetName = "flash"

centerDim = 6
childDim = 5
initSeed = "Random"

def run():
    # 设置超参数
    mode = "wgan"
    file_address = "data/final/flash/flashFinal_6_5.txt"
    log_path = "my.log"

    epoch = 100
    batch_size = 50
    g_learning_rate = 0.002#0.0005
    d_learning_rate = 0.001#0.0005

    # 生成器超参数
    g_input_size = 30     #随机噪声向量长度
    ######################################################################
    g_outputs = centerDim * (childDim + 1) #生成器的输出维度
    ######################################################################
    num_units = 25 # LSTM的个数，就是隐层中神经元的数量

    # 辨别器超参数
    ######################################################################
    d_input_size = centerDim * (childDim + 1)
    ######################################################################
    d_fc1 = 50
    d_fc2 = 25
    d_fc3 = 1


    # WGAN的参数
    CLIP = [-0.01, 0.01]
    CRITIC_NUM = 5
    lamda = 10

    D_rounds = 1
    G_rounds = 3
    # 生成z的函数
    def sample_Z(batch_size, latent_dim):
        return np.random.uniform(-1., 1., size=[batch_size, latent_dim])


    # 读取数据
    mm = MinMaxScaler(feature_range=(-1, 1))
    dataset = read_origin(file_address, centerDim, childDim)

    if len(dataset) < 50:
        print("len less than 50")
        return
    dataset = mm.fit_transform(dataset)
    samples_train = dataset


    # 建立一个三层辨别器
    class LstmCnnGan(object):
        def __init__(self, batch_size, d_input_size, g_input_size, g_learning_rate, d_learning_rate, d_fc1, d_fc2, d_fc3,
                     g_outputs,num_units, mode):
            # discriminator
            self.d_fc1 = d_fc1
            self.d_fc2 = d_fc2
            self.d_fc3 = d_fc3
            self.d_lr = d_learning_rate
            # generator
            self.num_units = num_units
            self.g_lr = g_learning_rate
            self.g_input_size = g_input_size
            self.g_outputs = g_outputs
            # all
            self.d_input_size = d_input_size
            self.batch_size = batch_size
            self.mode = mode

            with tf.name_scope("d_inputs"):
                self.d_xs = tf.placeholder(dtype=tf.float32, shape=[batch_size, d_input_size], name="d_xs")
            with tf.name_scope("g_inputs"):
                self.g_xs = tf.placeholder(dtype=tf.float32, shape=[None, g_input_size,1], name="g_xs")
                # self.g_ys = tf.placeholder(dtype=tf.float32, shape=[None, n_steps, g_outputs], name="g_ys")

            with tf.name_scope("build_model"):
                self.build_model()
            with tf.name_scope("train_op"):
                self.train_op_func()


    ################################辨别器######################################################
        def discriminator(self, d_xs):
            with tf.variable_scope("discriminator", reuse=tf.AUTO_REUSE) as scope:
                D_W1 = self._weight_variable(shape=[self.g_outputs, self.d_fc1], name="d_w1")
                D_b1 = self._bias_variable(shape=[self.d_fc1, ], name="d_b1")
                D_W2 = self._weight_variable(shape=[self.d_fc1, self.d_fc2], name="d_w2")
                D_b2 = self._bias_variable(shape=[self.d_fc2, ], name="d_b2")
                D_W3 = self._weight_variable(shape=[self.d_fc2, self.d_fc3], name="d_w3")
                D_b3 = self._bias_variable(shape=[self.d_fc3, ], name="d_b3")

                D_h1 = tf.nn.relu(tf.matmul(d_xs, D_W1) + D_b1)
                D_h2 = tf.nn.relu(tf.matmul(D_h1, D_W2) + D_b2)
                # D_h3 = tf.nn.relu(tf.matmul(D_h2, D_W3) + D_b3)
                d_output_logit = tf.matmul(D_h2, D_W3) + D_b3
                d_output = tf.nn.sigmoid(d_output_logit)


            return d_output_logit, d_output

    ################################生成器######################################################
        def generator(self, g_xs):
            with tf.variable_scope("generator") as scope:
                with tf.name_scope("g_lstm_layer"):
                    # lstm_cell = tf.contrib.rnn.BasicLSTMCell(self.g_cell_size)
                    # gru_cell = tf.contrib.rnn.GRUCell(self.n_cell_size, name="g_gru_cell")
                    lstm_cell = LSTMCell(num_units=self.num_units, state_is_tuple=True)
                    # with tf.name_scope("g_state_initializer"):
                    #     if self.g_init_state == None:
                    #         self.g_init_state = lstm_cell.zero_state(self.batch_size, dtype=tf.float32)
                    # self.g_cell_outputs, self.g_cell_final_states = tf.nn.dynamic_rnn(lstm_cell, g_xs,
                    #                                                               initial_state=self.g_init_state,
                    #                                                               time_major=False)
                    self.cell_outputs, self.cell_final_states = tf.nn.dynamic_rnn(
                        cell=lstm_cell,
                        dtype=tf.float32,
                        inputs=g_xs)
                # 添加输出层
                with tf.name_scope("g_output_layer"):
                    # 获取权重，偏置
                    W_out = self._weight_variable(shape=[self.num_units, self.g_outputs], name="g_output_weight")
                    b_out = self._bias_variable(shape=[self.g_outputs, ], name="g_output_bias")
                    # self.output = tf.matmul(self.cell_final_states[1], W_out) + b_out
                    l_out_X = tf.reshape(self.cell_outputs, [-1, self.num_units], name='g_out_2_2D')
                    with tf.name_scope('Wx_plus_b'):
                        g_output = tf.matmul(l_out_X, W_out) + b_out
                    g_output_prob = tf.nn.tanh(g_output)
            return g_output_prob

        # 建立model
        def build_model(self):
            self.G_output = self.generator(self.g_xs)
            self.D_real, self.D_real_logits = self.discriminator(self.d_xs)
            self.D_fake, self.D_fake_logits = self.discriminator(self.G_output)
            # 需要优化的参数
            self.t_vars = tf.trainable_variables()
            self.d_vars = [var for var in self.t_vars if 'discriminator' in var.name]
            self.g_vars = [var for var in self.t_vars if 'generator' in var.name]
            # 计算辨别器误差
            if self.mode == 'gan':
                with tf.name_scope('d_cost'):
                    self.D_real_loss = tf.reduce_mean(
                        tf.nn.sigmoid_cross_entropy_with_logits(logits=self.D_real_logits, labels=tf.ones_like(self.D_real_logits)))
                    tf.summary.scalar('d_real_cost', self.D_real_loss)

                    self.D_fake_loss = tf.reduce_mean(
                        tf.nn.sigmoid_cross_entropy_with_logits(logits=self.D_fake_logits, labels=tf.zeros_like(self.D_fake_logits)))
                    tf.summary.scalar('d_fake_cost', self.D_fake_loss)

                    self.D_loss = self.D_real_loss + self.D_fake_loss
                    tf.summary.scalar('d_loss', self.D_loss)
                # 计算生成器误差
                with tf.name_scope("g_loss"):
                    self.G_loss = tf.reduce_mean(
                        tf.nn.sigmoid_cross_entropy_with_logits(logits=self.D_fake_logits, labels=tf.ones_like(self.D_fake_logits)))
                    tf.summary.scalar('g_loss', tf.squeeze(self.G_loss))

                #     self.D_real_loss = tf.reduce_mean(tf.losses.huber_loss(logits=self.D_real_logits, labels=tf.ones_like(self.D_real_logits)))
                #     self.D_fake_loss = tf.reduce_mean(tf.losses.huber_loss(logits=self.D_fake_logits, labels=tf.zeros_like(self.D_fake_logits)))
                #     self.G_loss = tf.reduce_mean(tf.losses.huber_loss(logits=self.D_fake_logits, labels=tf.ones_like(self.D_fake_logits)))

            elif self.mode == 'wgan':
                with tf.name_scope("g_loss"):
                    self.G_loss = -tf.reduce_mean(self.D_fake_logits)  # 生成器loss
                    tf.summary.scalar('g_loss', tf.squeeze(self.G_loss))
                with tf.name_scope("d_loss"):
                    self.D_loss = tf.reduce_mean(self.D_fake_logits) - tf.reduce_mean(self.D_real_logits)  # 判别器loss
                    tf.summary.scalar('d_loss', self.D_loss)

        # 添加训练函数
        def train_op_func(self):
            if self.mode == 'gan':
                self.d_train_op = tf.train.AdamOptimizer(learning_rate=self.d_lr, beta1=0.5).minimize(self.D_loss, var_list=self.d_vars)
                self.g_train_op = tf.train.AdamOptimizer(learning_rate=self.g_lr, beta1=0.5).minimize(self.G_loss, var_list=self.g_vars)
            elif self.mode == 'wgan':
                self.d_train_op = tf.train.RMSPropOptimizer(learning_rate=self.d_lr).minimize(self.D_loss, var_list=self.d_vars)
                self.g_train_op = tf.train.RMSPropOptimizer(learning_rate=self.g_lr).minimize(self.G_loss, var_list=self.g_vars)
                clip_ops = []
                # 将判别器权重截断到[-0.01,0.01]
                for var in self.t_vars:
                    if var.name.startswith("discriminator"):
                        clip_bounds = CLIP
                        clip_ops.append(tf.assign(var, tf.clip_by_value(var, clip_bounds[0], clip_bounds[1])))
                self.clip_disc_weights = tf.group(*clip_ops)


        # 权重初始化的函数
        def _weight_variable(self, shape, name="weights"):
            initializer = 1
            if initSeed == "Random":
                initializer = tf.random_normal_initializer(mean=0., stddev=1.)
            else:
                initializer = tf.random_normal_initializer(mean=0., stddev=1.,seed=initSeed)
            weight = tf.get_variable(name=name, shape=shape, initializer=initializer)
            return weight

        # 偏置初始化函数
        def _bias_variable(self, shape, name="bias"):
            initializer = tf.constant_initializer(0.1)
            bias = tf.get_variable(name=name, shape=shape, initializer=initializer)
            return bias

    def subMain():

        # 搭建模型
        start = time.time()
        model = LstmCnnGan(batch_size, d_input_size, g_input_size, g_learning_rate, d_learning_rate, d_fc1, d_fc2, d_fc3,
                        g_outputs, num_units, mode)

        with tf.Session() as sess:
            saver = tf.train.Saver()
            merged = tf.summary.merge_all()
            sess.run(tf.global_variables_initializer())
            # 记录保存的文件
            j = 0
            # epoch = int(len(samples_train)/batch_size) - D_rounds - G_rounds
            d_loss_epoch = []
            g_loss_epoch = []
            cos_epoch = []  # 记录每次训练周期的余弦相似度
            euc_epoch = []  # 记录每次训练周期的欧氏距离

            # 当前数据集的batch大小
            batch = 2


            for i in range(epoch):
                for b in range(batch):
                    for d in range(D_rounds):
                        batch_ys = get_batch(samples_train, batch_size)
                        # 每次训练的数据
                        zs = sample_Z(batch_size, g_input_size).reshape(batch_size, g_input_size, 1)
                        # 生成器,辨别器的输入
                        feed_dict = {
                            model.g_xs: zs,
                            model.d_xs: batch_ys
                        }
                        # 计算误差 进行训练
                        d_loss, d_train_op, g_pred = sess.run(
                            [model.D_loss, model.d_train_op, model.G_output], feed_dict=feed_dict
                        )
                    d_loss_epoch.append(d_loss)
                    for g in range(G_rounds):
                        # 每次训练的数据
                        zs = sample_Z(batch_size, g_input_size).reshape(batch_size, g_input_size, 1)  # 生成器输出
                        feed_dict = {model.g_xs: zs}
                        # 计算误差 进行训练
                        g_loss, g_train_op, g_pred = sess.run(
                            [model.G_loss, model.g_train_op, model.G_output], feed_dict=feed_dict
                        )
                    g_loss_epoch.append(g_loss)

                    temp_gy = mm.inverse_transform(g_pred[0:batch_size])
                    temp_dx = mm.inverse_transform(batch_ys)
                    cosine = cos_similarity(temp_gy, temp_dx, batch_size)
                    cos_epoch.append(cosine[0][0])

                with open(log_path, mode='a+') as f:
                    if i % 10 == 0:
                        f.write('epoch' + str(i) + '--------------' + 'd_loss:' + str(d_loss) + ' ' + 'g_loss:' + str(g_loss) + ' ' + 'cosine:' + str(cosine[0][0]) + '--------------' + '\n')
                    f.close()

            end = time.time()
            with open(log_path, mode='a+') as f:
                f.write("循环运行时间:%.2f秒\n" % (end - start))
                f.close()

            # 对于数据进行处理
            # 由于添加了batch，所以总共有 epoch * batch 个数据
            # 这里我们的处理方式是取batch的平均值
            dLossEveEpoch = list()
            gLossEveEpoch = list()
            cosEveEpoch = list()
            for eveEpoch in range(epoch):
                sumDLoss = 0.0
                for i in range(batch):
                    sumDLoss += d_loss_epoch[eveEpoch * batch + i] / batch
                dLossEveEpoch.append(sumDLoss)

                sumGLoss = 0.0
                for i in range(batch):
                    sumGLoss += g_loss_epoch[eveEpoch * batch + i] / batch
                gLossEveEpoch.append(sumGLoss)

                sumCos = 0.0
                for i in range(batch):
                    sumCos += cos_epoch[eveEpoch * batch + i] / batch
                cosEveEpoch.append(sumCos)
            d_loss_epoch = dLossEveEpoch
            g_loss_epoch = gLossEveEpoch
            cos_epoch = cosEveEpoch

            # 进行绘制
            path = "out"
            ix = np.arange(epoch) + 1
            # 绘制loss
            fig = plt.figure(figsize=(6, 4))
            ax = fig.add_subplot(1, 1, 1)
            p1, = ax.plot(ix, d_loss_epoch, '-', alpha=.5, label='d_loss')
            ax.grid()
            ax.set_xlabel('epoch')
            ax.set_ylabel(r'd_loss')
            l1 = plt.legend([p1], ["d_loss"], loc='best')
            plt.ylim(0, 1)
            # 画图
            # plt.show()

            figPath = path + "/" + datasetName + "/" + datasetName + "DLoss_" + str(centerDim) + "_" + str(childDim) + "_" + str(initSeed) + ".png"
            fig.savefig(figPath)

            pingguFileName = path + "/" + datasetName + "/" + datasetName + "PingGu_" + str(centerDim) + "_" + str(childDim) + "_" + str(initSeed) + ".txt"
            with open(pingguFileName, 'a') as f:
                f.write("cos_epoch : " + str(cos_epoch) + "\n")
                f.write("d_loss_epoch : " + str(d_loss_epoch) + '\n\n')
                f.close()

            # 生成样本
            path1 = path + "/" + datasetName + "/" + datasetName + "Res_" + str(centerDim) + "_" + str(childDim) + "_" + str(initSeed) + ".txt"
            if os.path.exists(path1):
                os.remove(path1)
            for i in range(6):
                zs = sample_Z(batch_size, g_input_size).reshape(batch_size, g_input_size, 1)
                feed_dict = {model.g_xs: zs}
                g_pred = sess.run(model.G_output, feed_dict=feed_dict)
                temp_gy = mm.inverse_transform(g_pred[0:batch_size])
                res_list = temp_gy.tolist()
                with open(path1, 'a') as f:
                    for i in range(len(res_list)):
                        raw = [str(x) for x in res_list[i]]
                        res = ",".join(raw)
                        f.write(res + '\n')
        tf.reset_default_graph()
    subMain()
