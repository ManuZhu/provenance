import tensorflow.keras

def create():
    filters = 7
    kernel_size = 7
    #卷积核初始化：正态分布；偏置函数：常量初始化
    convolution_1d_layer1 = tensorflow.keras.layers.Conv1D(filters, kernel_size, kernel_initializer=tensorflow.keras.initializers.RandomNormal(mean = 0.0,stddev = 0.1),bias_initializer = "random_normal" ,strides=1, padding='same', input_shape= (256,1), activation="relu", name="convolution_1d_layer1")
    max_pooling_layer1 = tensorflow.keras.layers.MaxPool1D(pool_size=2, strides=2, padding='same', name="max_pooling_layer1")
    convolution_1d_layer2 = tensorflow.keras.layers.Conv1D(filters, kernel_size, kernel_initializer=tensorflow.keras.initializers.RandomNormal(mean = 0.0,stddev = 0.1),bias_initializer = "random_normal" , strides=1, padding='same', activation="relu", name="convolution_1d_layer2")
    max_pooling_layer2 = tensorflow.keras.layers.MaxPool1D(pool_size=2, strides=2, padding='same', name="max_pooling_layer2")
    convolution_1d_layer3 = tensorflow.keras.layers.Conv1D(filters, kernel_size, kernel_initializer=tensorflow.keras.initializers.RandomNormal(mean = 0.0,stddev = 0.1),bias_initializer = "random_normal" , strides=1, padding='same', activation="relu", name="convolution_1d_layer3")
    max_pooling_layer3 = tensorflow.keras.layers.MaxPool1D(pool_size=2, strides=2, padding='same', name="max_pooling_layer3")
    convolution_1d_layer4 = tensorflow.keras.layers.Conv1D(filters, kernel_size, kernel_initializer=tensorflow.keras.initializers.RandomNormal(mean = 0.0,stddev = 0.1),bias_initializer = "random_normal" , strides=1, padding='same', activation="relu", name="convolution_1d_layer4")
    max_pooling_layer4 = tensorflow.keras.layers.MaxPool1D(pool_size=2, strides=2, padding='same', name="max_pooling_layer4")
    reshape_layer = tensorflow.keras.layers.Flatten(name="reshape_layer")
    full_connect_layer = tensorflow.keras.layers.Dense(300,activation = "relu",kernel_initializer = tensorflow.keras.initializers.RandomNormal(mean = 0.0,stddev = 0.1),bias_initializer = "random_normal" ,use_bias = True,name="full_connect_layer")
    dropout_layer = tensorflow.keras.layers.Dropout(0.2, name = "dropout_layer")
    #输出大小：2
    softmax_layer = tensorflow.keras.layers.Dense(2,activation ="softmax" ,kernel_initializer = tensorflow.keras.initializers.RandomNormal(mean = 0.0 , stddev = 0.1),bias_initializer = "random_normal",use_bias = True,name="softmax_layer")

    model = tensorflow.keras.Sequential()
    model.add(convolution_1d_layer1)
    model.add(max_pooling_layer1)
    model.add(convolution_1d_layer2)
    model.add(max_pooling_layer2)
    model.add(convolution_1d_layer3)
    model.add(max_pooling_layer3)
    model.add(convolution_1d_layer4)
    model.add(max_pooling_layer4)
    model.add(reshape_layer)
    model.add(full_connect_layer)
    model.add(dropout_layer)
    model.add(softmax_layer)
    model.compile(loss = "categorical_crossentropy" , optimizer = 'Adam' , metrics = ['categorical_accuracy'])

    return model