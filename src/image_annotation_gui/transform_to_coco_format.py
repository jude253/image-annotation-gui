
import image_annotation_gui.utils as utils

if __name__ == '__main__':
    image_annotation_builder = utils.create_image_annotation_builder()
    image_annotation_builder.create_coco_format_data_archive()