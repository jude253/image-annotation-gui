import json
import os
from typing import List, Optional

from pydantic import BaseModel


# https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html#gacbaa02cffc4ec2422dfa2e24412a99e2
opencv_supported_formats = [
    ".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".png", 
    ".pbm", ".pgm", ".ppm", ".pxm", ".pnm", ".jp2",
    ".webp",
]


def find_dir_path(find_dir_name):
    cwd = os.getcwd()

    for root, dirs, files in os.walk(cwd):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if find_dir_name in dir_path:
                return dir_path


def is_image_file(file_path):
    return any([
        file_path.lower().endswith(img_ext) 
        for img_ext in opencv_supported_formats
    ])


def is_json_file(file_path):
    return file_path.lower().endswith('.json') 


def get_list_of_image_paths():
    image_data_dir_path = find_dir_path('image_data')
    image_paths = []

    for root, dirs, files in os.walk(image_data_dir_path):
        for file_name in files:
            full_file_path = os.path.join(root, file_name)

            if is_image_file(full_file_path):
                image_paths.append((root, file_name))
    
    return image_paths


class ImageAnnotation(BaseModel):
    image_full_path: str
    image_file_name: str
    layout_shapes_data_file_full_path: Optional[str]
    layout_shapes_data: Optional[dict]

    def write_layout_shapes_data_file(self):
        with open(self.layout_shapes_data_file_full_path, 'w') as f:
            f.write(json.dumps(self.layout_shapes_data, indent=2, default=str))
    
    def get_existing_layout_shapes_data_from_file(self):
        if os.path.exists(self.layout_shapes_data_file_full_path):
            with open(self.layout_shapes_data_file_full_path, 'r') as f:
                file_contents = f.read()
                # print(file_contents)
                self.layout_shapes_data = json.loads(file_contents)

    def update_layout_shapes_data(self, new_layout_shapes_data):
        self.layout_shapes_data = new_layout_shapes_data


    

class ImageAnnotationBuilder(BaseModel):
    image_annotations: List[ImageAnnotation] | None = None
    image_names: list[str] | None = None
    current_image_annotation: ImageAnnotation | None = None
    
    def setupImageAnnoations(self, image_paths):
        self.image_annotations = []
        self.image_names = []

        for image_path in sorted(image_paths):
            image_dir, image_file_name = image_path
            annotation_file_name = image_file_name.split('.')[0] + '.json'
            image_annotation = ImageAnnotation(
                image_full_path=os.path.join(image_dir, image_file_name),
                image_file_name=image_file_name,
                layout_shapes_data_file_full_path=os.path.join(image_dir, annotation_file_name),
                layout_shapes_data=None
            )
            image_annotation.get_existing_layout_shapes_data_from_file()

            self.image_annotations.append(image_annotation)
            self.image_names.append(image_file_name)

        self.current_image_annotation = self.image_annotations[0]
    
    def get_image_annotation_from_name(self, image_name):
        for image_annotation in self.image_annotations:
            if image_name == image_annotation.image_file_name:
                return image_annotation
        
        return None



def create_image_annotation_builder():
    image_annotation_builder = ImageAnnotationBuilder()
    image_paths = get_list_of_image_paths()
    image_annotation_builder.setupImageAnnoations(image_paths)
    return image_annotation_builder


if __name__ == '__main__':

    image_annotation_builder = create_image_annotation_builder()
    
    for imageAnnotation in image_annotation_builder.image_annotations:
        print(imageAnnotation)
