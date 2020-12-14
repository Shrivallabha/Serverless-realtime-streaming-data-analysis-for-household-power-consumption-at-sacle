import numpy as np
import pytest

import pandas as pd
import pandas._testing as tm


class TestDataFrameNamedAggregate:
    def test_agg_relabel(self):
        # GH 26513
        df = pd.DataFrame({"A": [1, 2, 1, 2], "B": [1, 2, 3, 4], "C": [3, 4, 5, 6]})

        # simplest case with one column, one func
        result = df.agg(foo=("B", "sum"))
        expected = pd.DataFrame({"B": [10]}, index=pd.Index(["foo"]))
        tm.assert_frame_equal(result, expected)

        # test on same column with different methods
        result = df.agg(foo=("B", "sum"), bar=("B", "min"))
        expected = pd.DataFrame({"B": [10, 1]}, index=pd.Index(["foo", "bar"]))

        tm.assert_frame_equal(result, expected)

    def test_agg_relabel_multi_columns_multi_methods(self):
        # GH 26513, test on multiple columns with multiple methods
        df = pd.DataFrame({"A": [1, 2, 1, 2], "B": [1, 2, 3, 4], "C": [3, 4, 5, 6]})
        result = df.agg(
            foo=("A", "sum"),
            bar=("B", "mean"),
            cat=("A", "min"),
            dat=("B", "max"),
            f=("A", "max"),
            g=("C", "min"),
        )
        expected = pd.DataFrame(
            {
                "A": [6.0, np.nan, 1.0, np.nan, 2.0, np.nan],
                "B": [np.nan, 2.5, np.nan, 4.0, np.nan, np.nan],
                "C": [np.nan, np.nan, np.nan, np.nan, np.nan, 3.0],
            },
            index=pd.Index(["foo", "bar", "cat", "dat", "f", "g"]),
        )
        tm.assert_frame_equal(result, expected)

    def test_agg_relabel_partial_functions(self):
        # GH 26513, test on partial, functools or more complex cases
        df = pd.DataFrame({"A": [1, 2, 1, 2], "B": [1, 2, 3, 4], "C": [3, 4, 5, 6]})
        result = df.agg(foo=("A", np.mean), bar=("A", "mean"), cat=("A", min))
        expected = pd.DataFrame(
            {"A": [1.5, 1.5, 1.0]}, index=pd.Index(["foo", "bar", "cat"])
        )
        tm.assert_frame_equal(result, expected)

        result = df.agg(
            foo=("A", min),
            bar=("A", np.min),
            cat=("B", max),
            dat=("C", "min"),
            f=("B", np.sum),
            kk=("B", lambda x: min(x)),
        )
        expected = pd.DataFrame(
            {
                "A": [1.0, 1.0, np.nan, np.nan, np.nan, np.nan],
                "B": [np.nan, np.nan, 4.0, np.nan, 10.0, 1.0],
                "C": [np.nan, np.nan, np.nan, 3.0, np.nan, np.nan],
            },
            index=pd.Index(["foo", "bar", "cat", "dat", "f", "kk"]),
        )
        tm.assert_frame_equal(result, expected)

    def test_agg_namedtuple(self):
        # GH 26513
        df = pd.DataFrame({"A": [0, 1], "B": [1, 2]})
        result = df.agg(
            foo=pd.NamedAgg("B", "sum"),
            bar=pd.NamedAgg("B", min),
            cat=pd.NamedAgg(column="B", aggfunc="count"),
            fft=pd.NamedAgg("B", aggfunc="max"),
        )

        expected = pd.DataFrame(
            {"B": [3, 1, 2, 2]}, index=pd.Index(["foo", "bar", "cat", "fft"])
        )
        tm.assert_frame_equal(result, expected)

        result = df.agg(
            foo=pd.NamedAgg("A", "min"),
            bar=pd.NamedAgg(column="B", aggfunc="max"),
            cat=pd.NamedAgg(column="A", aggfunc="max"),
        )
        expected = pd.DataFrame(
            {"A": [0.0, np.nan, 1.0], "B": [np.nan, 2.0, np.nan]},
            index=pd.Index(["foo", "bar", "cat"]),
        )
        tm.assert_frame_equal(result, expected)

    def test_agg_raises(self):
        # GH 26513
        df = pd.DataFrame({"A": [0, 1], "B": [1, 2]})
        msg = "Must provide"

        with pytest.raises(TypeError, match=msg):
            df.agg()
