"""Input functions for loading dataset."""
import tensorflow.compat.v2 as tf

# Constants for embeddings.
PADDING = 0
EOS = 1
UKN = 2
START = 3

MAX_WORD_NUM = 10


def parse(example_proto):
  """Parses the rico dataset."""
  feature_description = {
      'image/view_hierarchy/description/word_id':
          tf.io.FixedLenSequenceFeature([], tf.int64, allow_missing=True),
      'image/view_hierarchy/attributes/id/word_id':
          tf.io.FixedLenSequenceFeature([], tf.int64, allow_missing=True),
      'image/view_hierarchy/class/name/word_id':
          tf.io.FixedLenSequenceFeature([], tf.int64, allow_missing=True),
      'image/object/class/label':
          tf.io.FixedLenSequenceFeature([], tf.int64, allow_missing=True),
      'image/object/bbox/xmin':
          tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
      'image/object/bbox/xmax':
          tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
      'image/object/bbox/ymin':
          tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
      'image/object/bbox/ymax':
          tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
      'image/encoded':
          tf.io.FixedLenFeature([], tf.string),
  }

  example = tf.io.parse_single_example(example_proto, feature_description)

  # Map to DETR features
  coco_features = {}
  coco_features['image'] = tf.io.decode_png(
      example['image/encoded'], channels=3)
  h = tf.cast(tf.shape(coco_features['image'])[0], tf.float32)
  w = tf.cast(tf.shape(coco_features['image'])[1], tf.float32)

  obj_dict = {}
  coco_features['objects'] = obj_dict
  # x0, y0, x1, y1
  obj_dict['boxes'] = tf.stack([
      example['image/object/bbox/xmin'] * w,
      example['image/object/bbox/ymin'] * h,
      example['image/object/bbox/xmax'] * w,
      example['image/object/bbox/ymax'] * h,
  ],
                               axis=-1)

  obj_dict['desc_id'] = example['image/view_hierarchy/description/word_id']
  obj_dict['desc_id'] = tf.reshape(obj_dict['desc_id'], [-1, 10])
  obj_dict['resource_id'] = example[
      'image/view_hierarchy/attributes/id/word_id']
  obj_dict['resource_id'] = tf.reshape(obj_dict['resource_id'], [-1, 10])
  obj_dict['name_id'] = example['image/view_hierarchy/class/name/word_id']
  obj_dict['name_id'] = tf.reshape(obj_dict['name_id'], [-1, 10])

  obj_dict['label'] = example['image/object/class/label']
  # -1 is ROOT, valid label starts from 0.
  obj_dict['label'] = tf.maximum(obj_dict['label'], -1)
  # 1: invalid, 0: valid objects.
  obj_dict['binary_label'] = tf.cast(tf.equal(obj_dict['label'], 0), tf.int32)
  obj_dict['obj_mask'] = tf.ones_like(obj_dict['label'], dtype=tf.int32)

  return coco_features
