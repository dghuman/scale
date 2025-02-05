import numpy as np
import pandas as pd
import plotly as plt
import dash

# generate random dataset
data = pd.DataFrame(np.random.rand((100)))

app = dash.Dash(__name__)

app.layout = dash.html.Div(
    children=[
        dash.html.H1(children="test plot"),
        dash.html.P(
            children=(
                "a description for the test plot of random numbers"
            ),
        ),
        dash.dcc.Graph(
            figure={
                "data":[
                    {
                        "x":data.index,
                        "y":data[0],
                        "type":"lines",
                    },
                ],
                "layout":{"title":"random plot"},
            },
        )
    ]
)

app.run_server(debug=True)
