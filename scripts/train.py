from utils import *
from tensorflow.keras import optimizers
from tensorflow.keras import layers
from tensorflow import keras
import tensorflow as tf
import os
import numpy as np
import argparse


def get_training_data(images, landmark_list=[], blendshape_list=[]):
    all_input = []
    all_output = []
    all_data = []
    for idx, file in enumerate(images):
        tag = ('.').join(os.path.split(file)[-1].split('.')[:-1])
        pair_path = os.path.join(os.path.split(file)[0], tag + '.txt')
        blendshapes = []
        landmarks = []
        if not os.path.exists(pair_path):
            continue
        with open(pair_path, 'r') as f:
            lines = f.readlines()
            raw_blendshapes = lines[0].split(',')
            for bi in blendshape_list:
                blendshapes.append(float(raw_blendshapes[bi]))

            raw_landmarks = lines[1].split(' ')
            xmax = -1.0
            ymax = -1.0
            xmin = 2.0
            ymin = 2.0
            for l in raw_landmarks:
                coordinates = l.split(',')
                # landmarks.append([float(coordinates[0]), float(coordinates[1]), float(coordinates[2])])
                x = float(coordinates[0])
                y = float(coordinates[1])
                if x > xmax:
                    xmax = x
                if y > ymax:
                    ymax = y
                if x < xmin:
                    xmin = x
                if y < ymin:
                    ymin = y
            # print(xmin, ymin, xmax, ymax)
            for li in landmark_list:
                coordinates = raw_landmarks[li].split(',')
                # landmarks.append([float(coordinates[0]), float(coordinates[1]), float(coordinates[2])])
                x = float(coordinates[0])
                y = float(coordinates[1])
                # print(x,y)
                x = (x-xmin)/(xmax-xmin)
                y = (y-ymin)/(ymax-ymin)
                # print(x,y)
                landmarks.append([x, y])

        one_blendshapes = np.array(blendshapes)
        one_landmarks = np.array(landmarks)

        all_data.append([one_landmarks, one_blendshapes])
    # shuffle(all_data)
    for data in all_data:
        all_input.append(data[0])
        all_output.append(data[1])
    return np.array(all_input, dtype=np.float32), np.array(all_output, dtype=np.float32)


def preprocess_data(data_path):
    images = list_all_image(data_path)
    landmark_list = LEFT_EYEBROW_CONTOUR+LEFT_EYE_CONTOUR+LEFT_IRIS_CONTOUR + \
        RIGHT_EYEBROW_CONTOUR+RIGHT_EYE_CONTOUR+RIGHT_IRIS_CONTOUR+LIPS_CONTOUR
    blendshape_list = BROW_BLENDSHAPE+EYE_BLINK_BLENDSHAPE + \
        EYE_LOOK_BLENDSHAPE+MOUTH_BLENDSHAPE+JAW_BLENDSHAPE

    input, output = get_training_data(images, landmark_list, blendshape_list)
    return input, output


class BlendshapeAcc(keras.metrics.Metric):
    def __init__(self, name="blendshape_acc", **kwargs):
        super(BlendshapeAcc, self).__init__(name=name, **kwargs)
        self.total = self.add_weight(
            name='total', dtype=tf.float32, initializer=tf.zeros_initializer())
        self.count = self.add_weight(
            name='count', dtype=tf.float32, initializer=tf.zeros_initializer())

    def update_state(self, y_true, y_pred, sample_weight=None):
        accs = tf.where(tf.abs(y_true-y_pred) < 0.1, 1, 0)

        self.total.assign_add(tf.cast(tf.shape(y_true)[0], tf.float32))
        self.count.assign_add(tf.cast(tf.reduce_sum(
            accs), tf.float32)/tf.cast(tf.shape(y_pred)[1], tf.float32))

    def result(self):
        return self.count/self.total


def conv1d_sequential_heart_beat(model):
    model.add(layers.Conv1D(32, 8, strides=2,
                            activation='relu', padding='same'))
    model.add(layers.Conv1D(32, 8, strides=2,
                            activation='relu', padding='same'))
    model.add(layers.MaxPooling1D(3))
    model.add(layers.Conv1D(64, 8, strides=2,
                            activation='relu', padding='same'))
    model.add(layers.Conv1D(64, 8, strides=2,
                            activation='relu', padding='same'))
    model.add(layers.Conv1D(128, 4, strides=2,
                            activation='relu', padding='same'))
    model.add(layers.Conv1D(128, 4, strides=2,
                            activation='relu', padding='same'))
    model.add(layers.Conv1D(256, 2, strides=1,
                            activation='relu', padding='same'))
    model.add(layers.Conv1D(256, 2, strides=1,
                            activation='relu', padding='same'))
    model.add(layers.Dropout(0.5))
    model.add(layers.GlobalAveragePooling1D())
    return model


def export_tflite_model(checkpoint_dir):
    if os.path.exists(checkpoint_dir):
        converter = tf.lite.TFLiteConverter.from_saved_model(
            checkpoint_dir)  # path to the SavedModel directory
        tflite_model = converter.convert()
        lite_model_path = os.path.join(checkpoint_dir, 'model.tflite')
        with open(lite_model_path, 'wb') as f:
            f.write(tflite_model)
            print("export tflite model to", lite_model_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train_path",
        type=str,
        default='',
        help='Path to train data dir'
    )
    parser.add_argument(
        "--val_path",
        type=str,
        default='',
        help='Path to val data dir'
    )

    parser.add_argument(
        "--saved_model_dir",
        type=str,
        default=".",
        help='Path to save trained model'
    )
    parser.add_argument(
        "--loss",
        type=str,
        default="mse",
        help='Loss function'
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.1,
        help='Learning rate'
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1000,
        help='Training epochs'
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help='training batch size'
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help='network depth'
    )
    parser.add_argument(
        "--export_tflite_path",
        type=str,
        default='',
        help='checkpoint path to export tflite model'
    )

    args = parser.parse_args()

    export_saved_model_path = args.export_tflite_path
    if export_saved_model_path != '':
        if os.path.exists(export_saved_model_path):
            export_tflite_model(export_saved_model_path)
            return

    data_path = args.train_path
    saved_model_dir = args.saved_model_dir
    lr = args.lr
    epochs = args.epochs
    batch_size = args.batch_size
    loss = args.loss
    val_path = args.val_path
    depth = args.depth
    all_x, all_y = preprocess_data(data_path)
    val_x = []
    val_y = []
    if val_path != '':
        val_x, val_y = preprocess_data(val_path)
    val_rate = 0.1

    model = keras.Sequential()
    model.add(keras.Input(shape=all_x.shape[1:]))
    model = conv1d_sequential_heart_beat(model)
    model.add(layers.Dense(units=all_y.shape[1]))

    model.summary()
    model.compile(loss=loss, optimizer=optimizers.SGD(
        lr=lr), metrics=['mse', BlendshapeAcc()])
    x_train = []
    x_val = []
    y_train = []
    y_val = []

    if val_path != '':
        x_train = all_x
        y_train = all_y
        x_val = val_x
        y_val = val_y
    else:
        data_size = all_x.shape[0]
        train_rate = 1 - val_rate
        train_num = int(train_rate * data_size)
        x_train = all_x[:train_num]
        x_val = all_x[train_num:]
        y_train = all_y[:train_num]
        y_val = all_y[train_num:]

    tensorboard_callback = keras.callbacks.TensorBoard(
        log_dir=saved_model_dir, histogram_freq=1)
    checkpoint_dir = os.path.join(saved_model_dir, 'checkpoint')
    save_model_callback = keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_dir,
        save_best_only=True,
        monitor='val_loss',
        verbose=1
    )

    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(
        x_val, y_val), callbacks=[tensorboard_callback, save_model_callback])


if __name__ == "__main__":
    main()
