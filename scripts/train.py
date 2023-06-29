import argparse
import pathlib

import numpy as np
import tensorflow as tf

import indices


def preprocess_data(data_dir):
    inputs = []
    targets = []
    for p in pathlib.Path(data_dir).glob("**/*.txt"):
        if not p.is_file() or not p.with_suffix(".jpg").exists():
            continue
        lines = p.read_text().splitlines()

        landmarks = np.array([i.split(",") for i in lines[1].split(" ")], dtype=np.float32)
        landmarks = landmarks[:, :2]
        landmarks = (landmarks - landmarks.min(axis=0)) / (landmarks.max(axis=0) - landmarks.min(axis=0))
        landmarks = landmarks[indices.FACE_CONTOUR]
        inputs.append(landmarks)

        blendshapes = np.array(lines[0].split(","), dtype=np.float32)
        targets.append(blendshapes)

    return np.array(inputs, dtype=np.float32), np.array(targets, dtype=np.float32)


def build_model(input_dim, output_dim):
    model = tf.keras.Sequential()
    model.add(tf.keras.Input(shape=input_dim))
    model.add(tf.keras.layers.Conv1D(
        32, 8, strides=2, activation="relu", padding="same"))
    model.add(tf.keras.layers.Conv1D(
        32, 8, strides=2, activation="relu", padding="same"))
    model.add(tf.keras.layers.MaxPooling1D(3))
    model.add(tf.keras.layers.Conv1D(
        64, 8, strides=2, activation="relu", padding="same"))
    model.add(tf.keras.layers.Conv1D(
        64, 8, strides=2, activation="relu", padding="same"))
    model.add(tf.keras.layers.Conv1D(
        128, 4, strides=2, activation="relu", padding="same"))
    model.add(tf.keras.layers.Conv1D(
        128, 4, strides=2, activation="relu", padding="same"))
    model.add(tf.keras.layers.Conv1D(
        256, 2, strides=1, activation="relu", padding="same"))
    model.add(tf.keras.layers.Conv1D(
        256, 2, strides=1, activation="relu", padding="same"))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.GlobalAveragePooling1D())
    model.add(tf.keras.layers.Dense(units=output_dim))

    model.summary()
    return model


class BlendshapeAcc(tf.keras.metrics.Metric):
    def __init__(self, name="blendshape_acc", **kwargs):
        super(BlendshapeAcc, self).__init__(name=name, **kwargs)
        self.total = self.add_weight(
            name="total", dtype=tf.float32, initializer=tf.zeros_initializer())
        self.count = self.add_weight(
            name="count", dtype=tf.float32, initializer=tf.zeros_initializer())

    def update_state(self, y_true, y_pred, sample_weight=None):
        accs = tf.where(tf.abs(y_true - y_pred) < 0.1, 1, 0)
        self.total.assign_add(tf.cast(tf.shape(y_true)[0], tf.float32))
        self.count.assign_add(tf.cast(tf.reduce_sum(accs), tf.float32) /
                              tf.cast(tf.shape(y_pred)[1], tf.float32))

    def result(self):
        return self.count / self.total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_data_dir", dest="data_dir", default="./dataset",
        help="Path to the training data directory",
    )
    parser.add_argument(
        "--output_checkpoint_dir", dest="checkpoint_dir", default="./model/checkpoint",
        help="Path to the model checkpoint directory",
    )
    parser.add_argument(
        "--val_split", type=float, default=0.1,
        help="Split fraction to use as validation data",
    )
    parser.add_argument(
        "--learning_rate", type=float, default=0.1,
        help="Learning rate for model training",
    )
    parser.add_argument(
        "--batch_size", type=int, default=16,
        help="Batch size for model training",
    )
    parser.add_argument(
        "--epochs", type=int, default=1000,
        help="Number of epochs for model training",
    )
    args = parser.parse_args()

    inputs, targets = preprocess_data(args.data_dir)

    model = build_model(inputs.shape[1:], targets.shape[1])
    model.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=args.learning_rate),
        loss=tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.MeanSquaredError(), BlendshapeAcc()],
    )
    model.fit(
        x=inputs,
        y=targets,
        batch_size=args.batch_size,
        epochs=args.epochs,
        validation_split=args.val_split,
        callbacks=[tf.keras.callbacks.ModelCheckpoint(args.checkpoint_dir)],
    )
