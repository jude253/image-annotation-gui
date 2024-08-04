import plotly.express as px
from dash import Dash, dcc, html, Input, Output, no_update, callback
import json
import cv2
from image_annotation_gui.utils import ImageAnnotation, create_image_annotation_builder


def hello_world():
    return "Hello World"


current_state_text = ' '.join('''
At the moment, there is not way to adjust annotations once they are created.
However, it is possible to navigate away from an image, then navigate back
and create new annotations, which will overwrite the existing annotations.
The annotations that are written to disk are just dumps of the plotly
shapes json.  It also takes a while to load images and update the page.
I am not sure if there is something I can do to fix this, but showing
the user that the page is loading would be nice.  I imagine it will be
even slower with larger image files.
'''.split())


def get_shapes_json_list_from_fig(fig):
    """
    This could be used to save a copy of the current state of the shapes
    draw on the image.  The thinking behind this is that the
    "relayoutData" property doesn't return "shapes" in the dictionary
    when the size of the shape changes, so maybe saving a copy of the
    current shapes could work instead.  However, it's unclear how this
    updates in the figure and I am getting super confused looking at
    this.
    """
    shapes_json_list = []
    for shape in fig.select_shapes():
        shapes_json_list.append(json.loads(shape.to_json()))
    return shapes_json_list


def get_img_fig(current_image_annotation: ImageAnnotation):
    img_path = current_image_annotation.image_full_path
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fig = px.imshow(img)
    fig.update_layout(dragmode="drawrect")

    if current_image_annotation.layout_shapes_data:
        fig.update_layout(shapes=current_image_annotation.layout_shapes_data)
    
    return fig

image_annotation_builder = create_image_annotation_builder()
fig = get_img_fig(image_annotation_builder.current_image_annotation)

GRAPH_CONFIG = {
    "modeBarButtonsToAdd": [
        "drawrect",
        "eraseshape",
    ],
    "edits": {
        "annotationText": True
    }
}
GRAPH_PICTURE = dcc.Graph(id="graph-picture", figure=fig, config=GRAPH_CONFIG)
CURRENT_LABEL_VALUE = 'NONE'
app = Dash(__name__)
app.layout = html.Div(
    [   
        html.H1("Image Annotation GUI"),
        html.P(current_state_text),
        html.H3('Label Selector:'),
        dcc.Input(id="label-input", type="text", value=CURRENT_LABEL_VALUE, debounce=True),
        html.Div(id="current-label-value"),
        html.P("NOTE: Currently all annotations for an image will be set to have the same label.  It is intended to be set before creating an annotation."),
        html.H3("Image Selector:"),
        dcc.Dropdown(image_annotation_builder.image_names, image_annotation_builder.current_image_annotation.image_file_name, id='demo-dropdown'),
        html.Div(id='dd-output-container'),
        html.P("NOTE: It may take a moment to update to the image selected below"),
        html.H3("Drag and draw rectangle annotations:"),
        GRAPH_PICTURE,
        dcc.Markdown("Characteristics of shapes"),
        html.Pre(id="annotations-data"),
    ]
)

@callback(
    Output("current-label-value", "children"),
    Input("label-input", "value"),
)
def update_output(label_input_value):
    global CURRENT_LABEL_VALUE
    CURRENT_LABEL_VALUE = label_input_value
    return f'current-label-value: {label_input_value}'

@callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):

    return f'You have selected {value}'

@callback(
    Output('graph-picture', 'figure'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    image_annotation = image_annotation_builder.get_image_annotation_from_name(value)
    image_annotation_builder.current_image_annotation = image_annotation
    fig = get_img_fig(image_annotation)
    return fig



@callback(
    Output("annotations-data", "children"),
    Input("graph-picture", "relayoutData"),
    prevent_initial_call=False,
)
def on_new_annotation(relayout_data):
    current = image_annotation_builder.current_image_annotation
    if not relayout_data:
        return json.dumps(current.layout_shapes_data, indent=2)
    
    if "shapes" in relayout_data:
        current.update_layout_shapes_data(relayout_data['shapes'])

        # I can't figure out how to select one "shape" at a time, so update all of them
        for i, _ in enumerate(current.layout_shapes_data):
            current.layout_shapes_data[i]["label"]["text"] = CURRENT_LABEL_VALUE

    elif any(["shapes" in key for key in relayout_data]):

        # get `0` from `shapes[0].x0`, or whatever index is updated
        shape_index = int(str(
            [key for key in relayout_data if "x0" in key][0]
            ).split('[')[1].split(']')[0])
        
        x0 = int([relayout_data[key] for key in relayout_data if "x0" in key][0])
        x1 = int([relayout_data[key] for key in relayout_data if "x1" in key][0])
        y0 = int([relayout_data[key] for key in relayout_data if "y0" in key][0])
        y1 = int([relayout_data[key] for key in relayout_data if "y1" in key][0])

        # Update position of that shape
        current.layout_shapes_data[shape_index]['x0'] = x0
        current.layout_shapes_data[shape_index]['x1'] = x1
        current.layout_shapes_data[shape_index]['y0'] = y0
        current.layout_shapes_data[shape_index]['y1'] = y1

        # I can't figure out how to select one "shape" at a time, so update all of them
        for i, _ in enumerate(current.layout_shapes_data):
            current.layout_shapes_data[i]["label"]["text"] = CURRENT_LABEL_VALUE
        
    
    image_annotation_builder.current_image_annotation.write_layout_shapes_data_file()

    return json.dumps(current.layout_shapes_data, indent=2)

if __name__ == "__main__":
    app.run(debug=True)

