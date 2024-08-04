

from image_annotation_gui.utils import ImageAnnotationBuilder


def test_image_annotation_builder():
    test_file_ext = '.png'
    test_image_dir = 'a/b/c'
    image_paths = [
        (test_image_dir, f'img1{test_file_ext}'),
        (test_image_dir, f'img2{test_file_ext}')
    ]

    imageAnnotationBuilder = ImageAnnotationBuilder()
    imageAnnotationBuilder.setupImageAnnoations(image_paths)
    
    for imageAnnotation in imageAnnotationBuilder.image_annotations:
        assert test_image_dir in imageAnnotation.image_full_path
        assert imageAnnotation.image_file_name.endswith('.png')
        assert imageAnnotation.layout_shapes_data_file_full_path.endswith('.json')