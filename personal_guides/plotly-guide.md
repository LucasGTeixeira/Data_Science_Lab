# Plotly Guide

> A "when do I reach for this?" reference. Every section says what problem the
> chart or feature solves, then the code.

Plotly makes interactive charts — hover, zoom, pan — that live in notebooks, in
HTML files, and in dashboards. Choose it when you'll *explore* data (toggling
legend entries beats re-running a cell) or when the output is shared as an
interactive page. For static, print-quality figures matplotlib/seaborn are
lighter; plotly can still export PNGs if you want one tool for both.

Two APIs: `px` (Plotly Express) makes most charts in one line from a DataFrame;
`go` (graph objects) is the manual mode for mixed or finely-tuned figures.
Start with `px`; drop to `go` only when `px` can't express what you want.

## Setup

> **When:** every session. Import both APIs; add `kaleido` only if you'll
> export static images.

```python
import plotly.express as px          # high-level API (one line per chart)
import plotly.graph_objects as go    # low-level API (full control)
import pandas as pd

# install: pip install plotly kaleido   (kaleido only for static image export)

px.data.iris()                       # built-in sample datasets
# iris, tips, gapminder, stocks, wind, election, medal, gdp, carshare
```

`px` builds charts straight from DataFrames. `go` gives one class per trace
(`go.Scatter`, `go.Bar`, `go.Pie`, ...) for mixed/finely-tuned figures.

## Choosing a chart

> **When:** you have data and a question but aren't sure which chart answers
> it. Pick the row, then use the `px` example below.

| Question | Chart |
|---|---|
| How does it change over time? | `px.line` |
| Do two metrics move together? | `px.scatter` |
| How do categories compare? | `px.bar` |
| How is one variable distributed? | `px.histogram` / `px.box` / `px.violin` / `px.ecdf` |
| How has it changed by group over time? | `px.line` + `animation_frame` |
| What's the composition of a total? | `px.pie` / `px.sunburst` |
| How do many pairs correlate? | `px.imshow` |
| Where are the points? | `px.scatter_map` / `px.choropleth` |
| When did tasks happen? | `px.timeline` |

Distributions: histogram = shape, box = summary + outliers, violin = shape +
summary, ecdf = exact percentiles.

## Plotly Express: common plots

> **When:** any standard chart. One line each, straight from the DataFrame.

```python
# line — time series / trends
px.line(df, x="date", y="close", color="ticker", line_dash="ticker", markers=True)

# scatter — relationship between two numeric vars
px.scatter(df, x="total_bill", y="tip", color="sex", size="size", hover_data=["day"])

# bar — compare categories
px.bar(df, x="day", y="total_bill", color="sex", barmode="group")   # barmode: group|stack|relative

# histogram — distribution
px.histogram(df, x="total_bill", nbins=30, histnorm="probability density")

# box — distribution + outliers
px.box(df, x="day", y="total_bill", color="sex", points="outliers")

# violin — distribution shape (KDE) + box inside
px.violin(df, x="day", y="total_bill", color="sex", box=True, points="all")

# pie / donut — composition (few slices only)
px.pie(df, names="day", values="total_bill", hole=0.4)

# area — cumulative or stacked series
px.area(df, x="date", y="sales", color="region", groupnorm="fraction")

# heatmap from a matrix
px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu_r", aspect="auto")

# density heatmap from two columns
px.density_heatmap(df, x="total_bill", y="tip", nbinsx=20, nbinsy=20, marginal_x="histogram")

# strip / jitter — raw points per category
px.strip(df, x="day", y="total_bill", color="sex")

# ecdf — cumulative distribution
px.ecdf(df, x="total_bill", color="sex")

# 3D scatter
px.scatter_3d(df, x="sepal_length", y="sepal_width", z="petal_length", color="species")

# non-cartesian
px.sunburst(df, path=["continent", "country"], values="pop")        # or px.treemap
px.funnel(df, x="count", y="stage")
px.parallel_coordinates(df, color="species", dimensions=["sepal_length", "sepal_width"])
```

## Plotly Express: extras

> **When:** the basic chart isn't enough. Trendline for quick regression
> intuition, facets to compare groups side by side, animation to show time,
> maps for geographic data, timeline for schedules.

```python
# trendline + marginal distributions
px.scatter(df, x="total_bill", y="tip", trendline="ols",          # ols|lowess|rolling|ewm
           marginal_x="histogram", marginal_y="box")

# facets — small multiples
px.scatter(df, x="total_bill", y="tip", facet_row="time", facet_col="day")
px.scatter(df, x="total_bill", y="tip", facet_col="day", facet_col_wrap=3)

# animation over a column
px.scatter(gapminder, x="gdpPercap", y="lifeExp", size="pop", color="continent",
           animation_frame="year", animation_group="country",
           log_x=True, size_max=60, range_y=[20, 90])

# maps (no token needed with open-street-map)
px.choropleth(gapminder, locations="iso_alpha", color="lifeExp", animation_frame="year")
px.scatter_map(df, lat="lat", lon="lon", size="pop", color="region",
               map_style="open-street-map", zoom=3)

# timeline / gantt
df[["start", "end"]] = df[["start", "end"]].apply(pd.to_datetime)
px.timeline(df, x_start="start", x_end="end", y="task", color="task")
```

## Graph objects: mixed figures

> **When:** `px` can't do it — two y-axes, combining line + bar, precise
> control over each trace. Build the figure trace by trace.

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y1, mode="lines+markers", name="Sales"))
fig.add_trace(go.Bar(x=x, y=y2, name="Orders", yaxis="y2"))      # secondary axis

fig.update_layout(
    title="Revenue vs Orders",
    template="plotly_white",
    hovermode="x unified",                       # closest | x | x unified | y unified
    xaxis_title="Date", yaxis_title="Revenue",
    yaxis2=dict(title="Orders", overlaying="y", side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    height=500,
    bargap=0.3,
)
fig.update_xaxes(showgrid=False, tickangle=45, range=["2024-01-01", "2024-12-31"])
fig.update_yaxes(type="log", zeroline=True)
fig.update_traces(marker_size=10, selector=dict(type="bar"))     # target one trace class
fig.show()
```

Other useful `go` traces: `go.Histogram`, `go.Box`, `go.Violin`, `go.Pie`,
`go.Heatmap`, `go.Waterfall`, `go.Indicator`, `go.Candlestick`,
`go.Scatter3d`, `go.Scattergeo`, `go.Table`.

## Subplots

> **When:** comparing several views side by side — a small dashboard in one
> figure. `make_subplots` defines the grid; each trace goes to a `row`/`col`.

```python
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Line", "Bar", "Pie", "Scatter"),
    specs=[[{"type": "xy"}, {"type": "xy"}],
           [{"type": "domain"}, {"type": "xy"}]],   # domain = pie/indicator
    shared_xaxes=True,
)
fig.add_trace(go.Scatter(x=x, y=y1, name="A"), row=1, col=1)
fig.add_trace(go.Bar(x=x, y=y2, name="B"), row=1, col=2)
fig.add_trace(go.Pie(labels=l, values=v), row=2, col=1)
fig.add_trace(go.Scatter(x=x, y=y3, mode="markers"), row=2, col=2)
fig.update_layout(height=600, title_text="Panel", showlegend=False)
fig.show()
```

## Styling & defaults

> **When:** preparing figures for sharing — consistency matters. Set
> `px.defaults` once per session and every figure inherits the look.

```python
fig.update_layout(template="plotly_dark")
# templates: plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white, none

px.defaults.template = "plotly_white"                     # global default
px.defaults.color_discrete_sequence = px.colors.qualitative.Set2
px.defaults.color_continuous_scale = px.colors.sequential.Viridis
# qualitative: Plotly, Set1-3, Pastel, Dark2, Safe, Bold
# sequential:  Viridis, Plasma, Blues, Reds, YlGnBu
```

## Export & embed

> **When:** finishing a figure. `write_html` for interactive sharing (small
> file, libraries from CDN), `write_image` for reports/slides (needs kaleido),
> `write_json`/`to_dict` to hand the figure to another tool.

```python
fig.write_html("plot.html", include_plotlyjs="cdn")       # interactive, small file
fig.write_image("plot.png", width=1200, height=600, scale=2)   # needs kaleido
fig.write_json("plot.json")
fig.to_dict()                                             # figure as dict

fig.show(renderer="browser")      # open in browser (outside Jupyter)
fig.show(config=dict(displaylogo=False,                   # toolbar tweaks
                     modeBarButtonsToRemove=["lasso2d", "select2d"],
                     toImageButtonOptions=dict(format="png", scale=2)))
```

In JupyterLab the figure renders inline by default. `fig.show()` is not needed
if the figure is the last expression of a cell.

## Large data

> **When:** 100k+ points and the plot lags while zooming. WebGL renders on the
> GPU; beyond ~1M points, downsample before plotting.

```python
go.Scattergl(x=x, y=y)                    # WebGL renderer for 100k+ points
px.scatter(df, x="x", y="y", render_mode="webgl")
# ponytail: beyond ~1M points downsample first (df.sample / resample); plotly-resampler if needed
```

## Common errors

> **When:** the plot doesn't render or export. The usual suspects:

```
ValueError: Mime type rendering requires nbformat>=4.2.0 but it is not installed
  -> pip install nbformat  (Jupyter renderer)

ValueError: Invalid property ... / unsupported
  -> check argument spelling; use fig.full_figure_for_development() to inspect defaults

Kaleido requires Google Chrome / kaleido_get_chrome
  -> pip install -U kaleido; on servers use write_html instead of write_image
```

## Golden rules

- `px` first; drop to `go` only when px cannot express the figure.
- Data must be in **long format** for px: one row per observation, columns for x/y/color.
- Comment axis titles and units; totals are more readable than raw counts.
- `write_html` for sharing, `write_image` for reports (install `kaleido`).
- `px.defaults` + template = consistent look across every figure.
- Sorted data renders sorted lines; `fig.update_xaxes(categoryorder="total descending")` for bars.
