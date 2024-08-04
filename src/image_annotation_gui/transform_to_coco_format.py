
import os
import image_annotation_gui.utils as utils

if __name__ == '__main__':
    """
    In progress.  Too much stuff to do to finish this.

    https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/customization/object_detector.ipynb
    """
    image_data_dir = utils.find_dir_path('image_data')
    coco_format_data_dir = utils.find_dir_path('coco_format_data')
    image_batch_20240721 = utils.find_dir_path('image_batch_20240721')

    print(image_batch_20240721)
    for root, dirs, files in os.walk(image_batch_20240721):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if utils.is_json_file(file_path):
                with open(file_path, 'r') as f:
                    print(f.read())
    