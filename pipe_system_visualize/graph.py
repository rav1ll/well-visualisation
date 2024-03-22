import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[4, 1, 2],
    mode="markers + text",
    marker=dict(size=10),
    text=["Point A", "Point B", "Point C"],
    hoverinfo="text"  ,
    textposition="top center"
))
fig.update_layout(showlegend=False)
fig.show()
