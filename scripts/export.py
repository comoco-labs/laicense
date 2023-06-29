import argparse
import pathlib

import tensorflow as tf


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_checkpoint_dir", dest="checkpoint_dir", default="./model/checkpoint",
        help="Path to the model checkpoint directory",
    )
    parser.add_argument(
        "--output_model_file", dest="model_file", default="./model/model.tflite",
        help="Path to the exported model file",
    )
    args = parser.parse_args()
    
    converter = tf.lite.TFLiteConverter.from_saved_model(args.checkpoint_dir)
    tflite_model = converter.convert()

    p = pathlib.Path(args.model_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(tflite_model)
