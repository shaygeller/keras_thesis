from __future__ import print_function
import datetime
import keras
from keras.callbacks import EarlyStopping
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import os
import tensorflow as tf
import numpy as np


batch_size = 32
# num_classes = 10
epochs = 100
data_augmentation = True
save_dir = os.path.join(os.getcwd(), 'saved_filtered_models')
now = datetime.datetime.now()
curr_time = now.strftime("%Y%m%d%H%M")
model_name = 'keras_cifar10_filtered_trained_model_{0}_{1}_{2}.h5'.format(batch_size,epochs,curr_time)
print("Model name",model_name)


(x_train, _), (x_test, _) = cifar10.load_data()
num_classes = 10
train_filename = "train_filtered_data.txt.npy"
test_filename = "test_filtered_data.txt.npy"

y_train = np.load(train_filename)
y_test = np.load(test_filename)


print(y_train.shape)
print(y_test.shape)

x_train = x_train.astype('float32')
x_train /= 255
x_test = x_test.astype('float32')
x_test /= 255


model2 = Sequential()
model2.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_train.shape[1:]))

# initiate RMSprop optimizer
opt = keras.optimizers.rmsprop(lr=0.001, decay=1e-6)

# Let's train the model using RMSprop
model2.compile(loss='mean_squared_error',
              optimizer=opt,
              metrics=['accuracy'])


early_stopper = EarlyStopping(min_delta=0.001, patience=10)

if not data_augmentation:
    print('Not using data augmentation.')
    model2.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_test, y_test),
              shuffle=True,
              callbacks=[early_stopper])
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for feature-wise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(x_train)

    # Fit the model on the batches generated by datagen.flow().
    model2.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        epochs=epochs,
                        validation_data=(x_test, y_test),
                        workers=4,
                        callbacks=[early_stopper])

# Save model and weights
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model2.save(model_path)
print('Saved trained model at %s ' % model_path)
