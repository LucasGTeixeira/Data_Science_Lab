# Pandas Guide

> A "when do I reach for this?" reference. Every section starts with the job it
> does, then the code.

Pandas is for tabular data — the Excel you can script. The work usually goes
**load → inspect → clean → transform → group/merge → save**, which is the order
of the sections below. Two pairings carry most analyses: `groupby` for "per
group" questions, and `resample`/`rolling` for anything on a clock.

## Setup & I/O

> **When:** the start of every analysis (load) and the end (save). Read options
> at load time (`usecols`, `dtype`, `parse_dates`) save cleanup later — lazier
> than fixing types after the fact.

```python
import pandas as pd
import numpy as np

df = pd.read_csv("f.csv", usecols=["a", "b"], dtype={"id": str},
                 parse_dates=["date"], na_values=["", "NA"])
pd.read_csv("big.csv", chunksize=100_000)      # iterator of chunks
pd.read_parquet("f.parquet")                   # fast + typed
pd.read_excel("f.xlsx", sheet_name="Sheet1")
pd.read_json("f.json")
pd.read_sql("SELECT * FROM t", con=engine)

df.to_csv("out.csv", index=False)
df.to_parquet("out.parquet", compression="snappy")
df.to_excel("out.xlsx", index=False)
```

Which format? Parquet for intermediate data (compact, keeps dtypes, fast), CSV
for interchange with other tools, Excel when a stakeholder asked for it.
`dtype={"id": str}` is a common one: IDs like `"0012"` aren't numbers, and a
numeric dtype eats the leading zeros.

## Inspect

> **When:** immediately after loading, always. Two minutes here prevents an
> hour of debugging nonsense results. `info()` for dtypes/missingness,
> `describe()` for ranges/outliers, `value_counts()` for categorical sanity.

```python
df.head(); df.tail(); df.sample(5)
df.info()                          # dtypes + non-null counts
df.describe(include="all")
df.shape; df.columns; df.index; df.dtypes
df["col"].value_counts(dropna=False)
df["col"].value_counts(normalize=True)     # proportions
df.nunique(); df["col"].unique()
df.isna().sum()
df.duplicated().sum()
df.corr(numeric_only=True)
```

## Select & filter

> **When:** grabbing columns or subsetting rows — the most common operation.
> `.loc` speaks labels, `.iloc` speaks positions, boolean masks filter by
> condition.

```python
df["col"]                          # Series
df[["a", "b"]]                     # DataFrame
df.loc[2:5, "a":"c"]               # label based, end INCLUSIVE
df.iloc[0:5, 0:3]                  # position based, end EXCLUSIVE
df.at[3, "col"]; df.iat[0, 0]      # scalar access (fast)
df.filter(like="sales")            # columns by name
df.filter(regex="^val_")

df[df["age"] > 30]
df[(df["age"] > 30) & (df["city"] == "SP")]    # & | ~ ; parentheses required
df[df["city"].isin(["SP", "RJ"])]
df[df["age"].between(18, 30)]
df[df["name"].str.contains("ana", case=False, na=False)]
df[df["score"].notna()]
df.query("age > 30 and city == 'SP'")          # @var to use a local variable
```

The `loc`/`iloc` trap: `df.loc[10]` is the row *labeled* 10, `df.iloc[10]` is
the 11th row. Mixing them up is the classic off-by-one. `query()` is the
readable option for long conditions or when the threshold comes from a
variable (`@threshold`).

## Add, rename, drop

> **When:** creating derived columns, normalizing messy headers, deleting
> scratch columns. `assign` when you want to chain transformations.

```python
df["total"] = df["price"] * df["qty"]
df["tier"] = np.where(df["total"] > 100, "high", "low")
df = df.assign(total=df["price"] * df["qty"], double=lambda d: d["total"] * 2)

df.rename(columns={"old": "new"})
df.columns = [c.lower().strip() for c in df.columns]
df.drop(columns=["tmp"])
df.drop(index=[0, 1])
df.set_index("date")
df.reset_index(drop=True)
df["col"] = df["col"].astype("category")       # low-cardinality strings
```

## Sort & rank

> **When:** ordering rows for a report/plot, or finding top/bottom values.
> `rank` when you need a position or percentile rather than the value itself.

```python
df.sort_values("score", ascending=False)
df.sort_values(["dept", "score"], ascending=[True, False], na_position="last")
df.sort_index()
df.nlargest(5, "score"); df.nsmallest(5, "score")
df["score"].rank(method="dense", ascending=False)   # average|min|max|first|dense
```

## Missing data

> **When:** `isna().sum()` showed holes. First decide *why* they're missing:
> drop when few and random, fill when a default carries meaning, leave them
> alone when in doubt.

```python
df.isna().sum()
df.dropna()                                    # drop rows with any NaN
df.dropna(subset=["col"], how="all", thresh=2)
df.fillna(0)
df["col"].ffill(limit=1)                       # .bfill() ; fillna(method=) removed in pandas 3
df["col"].fillna(df["col"].median())
df["col"].interpolate(method="linear")
df.replace({-1: np.nan, "N/A": np.nan})
```

`ffill` is for time series where the last known value is a reasonable guess
(prices, sensor readings). Don't fill numeric columns with `0` by reflex — a
missing salary isn't zero, and it will drag your averages down.

## Duplicates

> **When:** one row per entity is expected and `duplicated().sum()` says
> otherwise. Check which row is correct before dropping — duplicates often
> hide a bug upstream.

```python
df.duplicated(subset=["id"], keep="first")
df.drop_duplicates(subset=["id"], keep="last")
df["col"].drop_duplicates()
```

## GroupBy & aggregation

> **When:** any "per group" question — average per department, count per day,
> top N per category. Mental model: **split** rows by key, **apply** a
> function, **combine** the results.

```python
df.groupby("dept")["salary"].mean()
df.groupby(["dept", "level"], as_index=False)["salary"].sum()     # as_index=False -> column
df.groupby("dept", dropna=False).size()                           # rows per group, keeps NaN

df.groupby("dept").agg(                                           # named aggregation
    total=("salary", "sum"),
    avg=("salary", "mean"),
    n=("salary", "size"),
)
df.groupby("dept")["salary"].agg(["count", "mean", "std", "min", "max"])
df.groupby("dept").agg({"salary": "mean", "age": "max"})          # dict form

df.groupby("dept")["salary"].transform("mean")                    # same length as df
df["diff"] = df["salary"] - df.groupby("dept")["salary"].transform("mean")
df.groupby("dept").filter(lambda g: g["salary"].mean() > 5000)
df.groupby("dept").apply(lambda g: g.nlargest(2, "salary"), include_groups=False)
df.groupby("dept").cumsum()        # also .cumcount(), .rank(), .shift()
df.groupby("dept")["salary"].value_counts(normalize=True)
```

Choosing the operation:

- `agg` → one row per group (summary tables).
- `transform` → same shape as the original, values broadcast back (e.g. add a
  "deviation from group mean" column).
- `filter` → keep or drop whole groups.
- `apply` → arbitrary function per group; most flexible, slowest, use last.

## Merge & join

> **When:** combining two tables that share a key — orders + customers, sales +
> product catalog. This is where silent row duplication bites, so always
> verify the result.

```python
pd.merge(orders, customers, on="cust_id", how="left")
pd.merge(a, b, left_on="id", right_on="customer_id", how="inner")
pd.merge(a, b, on="id", suffixes=("_x", "_y"), indicator=True)     # _merge column
pd.merge(a, b, on="id", validate="many_to_one")                    # 1:1|1:m|m:1|m:m
# how: inner, left, right, outer, cross

a.join(b.set_index("id"), on="id", how="left")    # index-based join
# indicator "_merge": both / left_only / right_only -> detect unmatched rows
```

`left` keeps every left row (attach info where it exists); `inner` keeps only
matches. Use `validate=` (asserts the relationship is 1:1/m:1) and
`indicator=True` (labels each row both/left_only/right_only), then compare the
row count before and after. If it changed unexpectedly, your key isn't unique
on one side. `merge` is the general tool (columns as keys); `join` is merge on
the index.

## Concat / combine

> **When:** `concat` when tables share columns and you're stacking them
> (monthly files into a year). Different tool from `merge`: no keys involved,
> just glue.

```python
pd.concat([df1, df2], ignore_index=True)          # stack rows
pd.concat([df1, df2], axis=1)                     # side by side (aligns on index)
pd.concat([df1, df2], keys=["2024", "2025"])      # tag source in a MultiIndex
df1.combine_first(df2)                            # fill df1's NaNs from df2
```

## Reshape

> **When:** the data's orientation doesn't match the tool. Pivot = long → wide
> (one row per entity, a column per category). Melt = wide → long, which is the
> format Plotly Express needs (one row per observation).

```python
df.pivot(index="date", columns="ticker", values="close")
df.pivot_table(index="dept", columns="level", values="salary",
               aggfunc="mean", fill_value=0, margins=True)
df.melt(id_vars="id", value_vars=["a", "b"], var_name="key", value_name="value")
df.explode("tags")                                # list cell -> one row per item
pd.crosstab(df["dept"], df["level"], normalize="index")
pd.get_dummies(df, columns=["city"], drop_first=True)
df.stack(); df.unstack()
```

## Strings

> **When:** cleaning text — trimming whitespace, standardizing case, splitting
> one column into several, extracting patterns. `.str` is vectorized; no loops.

```python
s = df["name"]
s.str.lower(); s.str.strip(); s.str.title()
s.str.contains("ana", case=False, na=False)
s.str.replace(r"\s+", "_", regex=True)
s.str.split(",", expand=True)             # -> DataFrame with one column per part
s.str.extract(r"(\d{4})-(\d{2})")         # capture groups -> columns
s.str.startswith("A"); s.str.len(); s.str[:3]
s.str.zfill(5); s.str.cat(sep=", ")
```

## Dates & time series

> **When:** anything time-based. First rule: `pd.to_datetime` early — as long
> as it's a string, nothing works. Then `dt` for per-row parts, `resample` for
> regular time buckets, `rolling` for smoothing, `shift`/`diff`/`pct_change`
> for changes.

```python
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
df["year"] = df["date"].dt.year
df["dow"] = df["date"].dt.day_name()
df["week"] = df["date"].dt.isocalendar().week
df["date"].dt.strftime("%Y-%m")
df["date"].dt.to_period("M")                      # month buckets

df = df.set_index("date").sort_index()
df.resample("ME")["sales"].sum()                  # month-end ("M" deprecated)
df.resample("W").agg({"sales": "sum", "price": "mean"})

df["sales"].rolling(7).mean()                     # 7-period moving average
df["sales"].expanding().max()
df["sales"].ewm(span=7).mean()                    # exponential weighting

df["sales"].shift(1); df["sales"].diff(); df["sales"].pct_change()
df.index.tz_localize("UTC").tz_convert("America/Sao_Paulo")
pd.date_range("2024-01-01", periods=12, freq="ME")
```

`resample` and `rolling` need a sorted `DatetimeIndex` — that's the
`set_index().sort_index()` step, easy to forget and produces silently wrong
results when skipped.

## Apply, map, pipe

> **When:** custom transformations pandas doesn't have built in. Reach in this
> order: `map` (dict/Series lookup) → `apply` on a Series (element logic) →
> `apply(axis=1)` (rows; slow, last resort) → `pipe` to chain whole-frame steps.

```python
df["col"].map({"A": 1, "B": 2})       # dict / Series mapping (unmatched -> NaN)
df["col"].map(lambda x: x * 2)
df["col"].apply(func)                 # element-wise on a Series
df.apply(func, axis=1)                # row-wise (use sparingly, slow)
df.map(func)                          # element-wise whole frame (pandas 2.1+)
df.pipe(clean).pipe(features)         # chain fns, df passed as first arg
```

## Binning

> **When:** turning a continuous column into categories — age bands, income
> quartiles, risk tiers. `cut` when you know the boundaries, `qcut` when you
> want equal-sized groups.

```python
pd.cut(df["age"], bins=[0, 18, 35, 60, 100],
       labels=["teen", "young", "adult", "senior"])
pd.qcut(df["income"], q=4, labels=["Q1", "Q2", "Q3", "Q4"])   # equal-size buckets
```

## Performance

> **When:** code is slow, or data no longer fits comfortably in memory. First
> rule: never loop rows for arithmetic — vectorize.

```python
# vectorize — no row loops for arithmetic
df["c"] = df["a"] + df["b"]

df["city"] = df["city"].astype("category")        # repeated strings -> codes
df["n"] = pd.to_numeric(df["n"], downcast="integer")

for row in df.itertuples(index=False): ...        # itertuples > iterrows
pd.read_csv("f.csv", usecols=[...], dtype={...})  # load less, parse once
```

## Golden rules

- Prefer `.loc`/boolean masks over chained indexing (`df[df.a > 0]["b"] = 1` may not stick).
- Avoid `inplace=True`; assign the result (`df = df.dropna()`).
- Validate merges: `validate=` + `indicator=True` before trusting the row count.
- `agg` = one row per group; `transform` = broadcast; `filter` = subset groups.
- `resample`/`rolling` need a sorted `DatetimeIndex` (`set_index().sort_index()`).
- Never loop rows for math — vectorize; pandas 2.2+ runs with Copy-on-Write semantics.
