# python3
#
# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example using TF Lite to detect objects with the Raspberry Pi camera."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import re
import time

from annotation import Annotator
from gpiozero import LED

import numpy as np
import picamera

from PIL import Image
from tflite_runtime.interpreter import Interpreter

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


def load_labels(path):
  """Loads the labels file. Supports files with or without index numbers."""
  with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    labels = {}
    for row_number, content in enumerate(lines):
      pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
      if len(pair) == 2 and pair[0].strip().isdigit():
        labels[int(pair[0])] = pair[1].strip()
      else:
        labels[row_number] = pair[0].strip()
  return labels


def set_input_tensor(interpreter, image):
  """Sets the input tensor."""
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def get_output_tensor(interpreter, index):
  """Returns the output tensor at the given index."""
  output_details = interpreter.get_output_details()[index]
  tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
  return tensor

def intersect(box):
  hotspot_width = 140

  #r2
  h_xmin = int ((CAMERA_WIDTH - hotspot_width) / 2)
  h_xmax = int (h_xmin + hotspot_width)
  h_ymin = int ((CAMERA_HEIGHT - hotspot_width) / 2)
  h_ymax = int (h_ymin + hotspot_width)

  #r1
  ymin, xmin, ymax, xmax = box
  xmin = int(xmin * CAMERA_WIDTH)
  xmax = int(xmax * CAMERA_WIDTH)
  ymin = int(ymin * CAMERA_HEIGHT)
  ymax = int(ymax * CAMERA_HEIGHT)

  #print("HS", h_xmin, h_xmax, h_ymin, h_ymax, sep=",")
  #print("BB", xmin, xmax, ymin, ymax, sep=",")




# "left", the x coordinate of its left side,
# "top", the y coordinate of its top side,
# "right", the x coordinate of its right side,
# "bottom", the y coordinate of its bottom side,

# function IntersectRect(r1:Rectangle, r2:Rectangle):Boolean {
#     return !(r2.left > r1.right
#         || r2.right < r1.left
#         || r2.top > r1.bottom
#         || r2.bottom < r1.top);
# }

 # left = 1
 # right = 3
 # top = 2
 # bottom = 0

  return not(h_xmin > xmax or h_xmax < xmin or h_ymax < ymin or h_ymin > ymax)


def detect_objects(interpreter, image, threshold):
  """Returns a list of detection results, each a dictionary of object info."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()

  # Get all output details
  boxes = get_output_tensor(interpreter, 0)
  classes = get_output_tensor(interpreter, 1)
  scores = get_output_tensor(interpreter, 2)
  count = int(get_output_tensor(interpreter, 3))

  results = []
  for i in range(count):
    # We don't have birds or dogs in the gallery - always mark them as people.
    if scores[i] >= threshold and (classes[i] == 0 or classes[i] == 15 or classes[i] == 16 or classes[i] == 17) and intersect(boxes[i]):
      result = {
          'bounding_box': boxes[i],
          'class_id': 0,
          'score': scores[i]
      }
      results.append(result)
  return results


def annotate_objects(annotator, results, labels):
  """Draws the bounding box and label for each object in the results."""
  for obj in results:
    # Convert the bounding box figures from relative coordinates
    # to absolute coordinates based on the original resolution
    ymin, xmin, ymax, xmax = obj['bounding_box']
    xmin = int(xmin * CAMERA_WIDTH)
    xmax = int(xmax * CAMERA_WIDTH)
    ymin = int(ymin * CAMERA_HEIGHT)
    ymax = int(ymax * CAMERA_HEIGHT)

    # Overlay the box, label, and score on the camera preview
    annotator.bounding_box([xmin, ymin, xmax, ymax])
    annotator.text([xmin, ymin],
                   '%s\n%.2f' % (labels[obj['class_id']], obj['score']))


def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  parser.add_argument(
      '--threshold',
      help='Score threshold for detected objects.',
      required=False,
      type=float,
      default=0.4)
  args = parser.parse_args()

  labels = load_labels(args.labels)
  interpreter = Interpreter(args.model)
  interpreter.allocate_tensors()
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']
  led = LED(14)

  with picamera.PiCamera(
      resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
    camera.start_preview()
    camera.capture('test.jpg');

    last_time = time.time_ns()
    on = False
    try:
      stream = io.BytesIO()
      annotator = Annotator(camera)
      for _ in camera.capture_continuous(
          stream, format='jpeg', use_video_port=True):
        stream.seek(0)
        image = Image.open(stream).convert('RGB').resize(
            (input_width, input_height), Image.ANTIALIAS)
        start_time = time.monotonic()
        results = detect_objects(interpreter, image, args.threshold)
        elapsed_ms = (time.monotonic() - start_time) * 1000

        # If we have detected something that looks like a person - toggle the
        # relay.
        if len(results) == 0 and on:
          on = False
          last_time = time.time_ns()
        elif len(results) > 0:
          on = True
          led.on()

        delta_t = (time.time_ns() - last_time) / 1000000000
        if not on and delta_t > 1.0:
           led.off()

        # If we have detected something that looks like a person - toggle the
        # relay.
        # if len(results) == 0:
        #     led.off()
        # else:
        #     led.on()

        annotator.clear()
        annotate_objects(annotator, results, labels)
        annotator.text([5, 0], '%.1fms' % (elapsed_ms))
        annotator.update()

        stream.seek(0)
        stream.truncate()

    finally:
      camera.stop_preview()


if __name__ == '__main__':
  main()
