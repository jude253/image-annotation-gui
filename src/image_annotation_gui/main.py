import plotly.express as px
from dash import Dash, dcc, html, Input, Output, no_update, callback
from skimage import io
import json

from image_annotation_gui.utils import create_image_annotation_builder


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


image_annotation_builder = create_image_annotation_builder()
img = io.imread(image_annotation_builder.current_image_annotation.image_full_path)
fig = px.imshow(img)
fig.update_layout(dragmode="drawrect")

app = Dash(__name__)
app.layout = html.Div(
    [   
        html.H1("Image Annotation GUI"),
        html.P(current_state_text),
        html.H3("It may take a moment to update to the image selected below"),
        dcc.Dropdown(image_annotation_builder.image_names, image_annotation_builder.current_image_annotation.image_file_name, id='demo-dropdown'),
        html.Div(id='dd-output-container'),
        html.H3("Drag and draw rectangle annotations"),
        dcc.Graph(id="graph-picture", figure=fig),
        dcc.Markdown("Characteristics of shapes"),
        html.Pre(id="annotations-data"),
    ]
)

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
    img = io.imread(image_annotation.image_full_path)
    fig = px.imshow(img)
    fig.update_layout(dragmode="drawrect")
    return fig


@callback(
    Output("annotations-data", "children"),
    Input("graph-picture", "relayoutData"),
    prevent_initial_call=True,
)
def on_new_annotation(relayout_data):
    if "shapes" in relayout_data:
        image_annotation_builder.current_image_annotation.write_annotation_file(relayout_data["shapes"])
        return json.dumps(relayout_data["shapes"], indent=2)
    else:
        return no_update

if __name__ == "__main__":
    app.run(debug=True)

