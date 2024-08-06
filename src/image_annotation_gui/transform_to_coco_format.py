
import image_annotation_gui.utils as utils

if __name__ == '__main__':
    # For now no shuffling, but could add in the future
    image_annotation_builder = utils.create_image_annotation_builder()
    
    num_files = len(image_annotation_builder.image_annotations)

    validataion_data_set_size = num_files//10*2  # 20%
    training_data_set_size = num_files - validataion_data_set_size  # 80%
    
    training_image_annotation_builder = utils.ImageAnnotationBuilder(
        image_annotations=image_annotation_builder.image_annotations[:training_data_set_size]
    )
    validation_image_annotation_builder = utils.ImageAnnotationBuilder(
        image_annotations=image_annotation_builder.image_annotations[training_data_set_size:]
    )
    print('Training Data Set Size:', len(training_image_annotation_builder.image_annotations))
    print('Validation Data Set Size:', len(validation_image_annotation_builder.image_annotations))
    training_image_annotation_builder.create_coco_format_data_archive('training')
    validation_image_annotation_builder.create_coco_format_data_archive('validation')

    # image_annotation_builder.create_coco_format_data_archive()