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

def find_image_data_dir_path():
    cwd = os.getcwd()

    for root, dirs, files in os.walk(cwd):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if 'image_data' in dir_path:
                return dir_path


def get_list_of_image_paths():
    image_data_dir_path = find_image_data_dir_path()
    image_paths = []

    for root, dirs, files in os.walk(image_data_dir_path):
        for file_name in files:
            full_file_path = os.path.join(root, file_name)

            if any([
                full_file_path.lower().endswith(img_ext) 
                for img_ext in opencv_supported_formats
            ]):
                image_paths.append((root, file_name))
    
    return image_paths


class ImageAnnotation(BaseModel):
    image_full_path: str
    image_file_name: str
    annotation_file_full_path: Optional[str]

    def write_annotation_file(self, write_json):
        with open(self.annotation_file_full_path, 'w') as f:
            f.write(json.dumps(write_json, indent=2, default=str))

    

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
                annotation_file_full_path=os.path.join(image_dir, annotation_file_name),
            )

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
