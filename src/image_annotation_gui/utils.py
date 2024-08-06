import json
import os
import shutil
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


def get_coco_data_set_dir(data_set_name, data_set_parent_folder=''):
    coco_root = find_dir_path('coco_format_data')
    data_set_dir = os.path.join(coco_root, data_set_parent_folder, data_set_name)

    # Apparently the folder expected is `images` not `data`
    # https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/model_maker/python/vision/object_detector/dataset.py#L29-L88
    images_dir = os.path.join(data_set_dir, 'images')

    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    return data_set_dir
        

class Category(BaseModel):
    id: int
    name: str

class Image(BaseModel):
    id: int
    file_name: str  # jpeg

class BoundingBox(BaseModel):
    x: float  # top left
    y: float  # top left
    w: float
    h: float

    def to_list(self):
        return [self.x, self.y, self.w, self.h]

class Annotation(BaseModel):
    id: int
    image_id: int
    category_id: int
    bbox: list[float]

class LabelsJson(BaseModel):
    """
    This class only has what is needed for the media pipes training:
    https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/customization/object_detector.ipynb
    
    
    https://cocodataset.org/#format-data
    """
    categories: list[Category]
    images: list[Image]
    annotations: list[Annotation]

    def get_image_id(self, file_name):
        image_id = None
        for image in self.images:
            if file_name == image.file_name:
                image_id = image.id
                break
        
        if image_id is None:
            new_image = Image(
                id=len(self.images),
                file_name=file_name
            )
            self.images.append(new_image)
            image_id = new_image.id

        return image_id
    
    def get_category_id(self, category_name):
        category_id = None
        for category in self.categories:
            if category_name == category.name:
                category_id = category.id
                break
        
        if category_id is None:
            new_category = Category(
                id=len(self.categories)+1,  # 0 is reserved!
                name=category_name
            )
            self.categories.append(new_category)
            category_id = new_category.id

        return category_id
    
    def add_annotation(self, annotation):
        self.annotations.append(annotation)

    def to_json(self):
        return json.dumps({
            "categories": [c.__dict__ for c in self.categories],
            "images": [i.__dict__ for i in self.images],
            "annotations": [a.__dict__ for a in self.annotations],
        })
    
    def write_file(self, data_set_name, data_set_parent_folder=''):
        data_dir = get_coco_data_set_dir(data_set_name, data_set_parent_folder=data_set_parent_folder)
        labels_json_file_path = os.path.join(data_dir, 'labels.json')

        with open(labels_json_file_path, 'w') as file:
            file.write(self.to_json())


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
    labels_json: LabelsJson | None = None
    
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
    
    def set_labels_json(self):
        labels_json = LabelsJson(
            categories=[],
            images=[],
            annotations=[]
        )
        for image_annotation in self.image_annotations:
            layout_shapes_data = image_annotation.layout_shapes_data
            for layout_shape in layout_shapes_data:
                x0 = layout_shape['x0']
                y0 = layout_shape['y0']
                x1 = layout_shape['x1']
                y1 = layout_shape['y1']
                x_top_left = min(x0, x1)
                y_top_left = min(y0, y1)
                w = abs(x1 - x0)
                h = abs(y1 - y0)
                bbox = BoundingBox(
                    x=x_top_left,
                    y=y_top_left,
                    w=w,
                    h=h
                )
                category_name = layout_shape['label']['text']
                category_id = labels_json.get_category_id(category_name)
                image_id = labels_json.get_image_id(image_annotation.image_file_name)
                annotation = Annotation(
                    id=len(labels_json.annotations),
                    image_id=image_id,
                    category_id=category_id,
                    bbox=bbox.to_list()
                )
                labels_json.add_annotation(annotation)
        self.labels_json = labels_json

    def create_coco_format_data_archive(self, data_set_name, data_set_parent_folder=''):
        """
        Create a zip file of the coco format data
        """
        data_set_dir = get_coco_data_set_dir(data_set_name, data_set_parent_folder=data_set_parent_folder)
        self.set_labels_json()
        self.labels_json.write_file(data_set_name, data_set_parent_folder=data_set_parent_folder)

        for image_annotation in self.image_annotations:
            old_image_file_path = image_annotation.image_full_path
            new_image_file_path = os.path.join(data_set_dir, 'images', image_annotation.image_file_name)
            shutil.copyfile(old_image_file_path, new_image_file_path)

        shutil.make_archive(data_set_dir, 'zip', data_set_dir)
        shutil.rmtree(data_set_dir)


def create_image_annotation_builder():
    image_annotation_builder = ImageAnnotationBuilder()
    image_paths = get_list_of_image_paths()
    image_annotation_builder.setupImageAnnoations(image_paths)
    return image_annotation_builder


if __name__ == '__main__':

    image_annotation_builder = create_image_annotation_builder()
    
    for image_annotation in image_annotation_builder.image_annotations:
        print(image_annotation)
