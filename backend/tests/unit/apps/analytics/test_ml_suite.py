"""Focused ML tests: observable behaviour of the analytics toolkit.

Covers Linear Regression, Decision Tree, Random Forest, KNN, K-Means
(via recommender.kmeans), binary + multiclass classification, confusion
matrices, classification/regression metrics, scaling, train/test splits
and regression evaluation — plus edge cases (empty input, too few rows,
single class, constant features, >2 classes, missing values).
"""

import math

import pytest

from apps.analytics.ml import evaluate
from apps.analytics.ml.evaluate import (
    classification_scores,
    confusion_matrix,
    confusion_matrix_multiclass,
    mean_absolute_error,
    r2_score,
    regression_scores,
)
from apps.analytics.ml.forest import RandomForestClassifier
from apps.analytics.ml.knn import KNNClassifier
from apps.analytics.ml.linear import LinearRegression
from apps.analytics.ml.preprocessing import (
    StandardScaler,
    stratified_split,
    train_test_split,
)
from apps.analytics.ml.tree import DecisionTreeClassifier
from apps.analytics.recommender import (
    affinity_matrix,
    jaccard,
    kmeans,
    recommend,
    recommendation_reason,
)


# ---------------------------------------------------------------- helpers

def binary_dataset():
    # Clearly separable: x < 5 → 0, x >= 5 → 1.
    X = [[float(i)] for i in range(10)] * 4
    y = [0 if i < 5 else 1 for i in range(10)] * 4
    return X, y


def multiclass_dataset():
    # Three bands on one feature: [0,2] → 0, [3,5] → 1, [6,8] → 2.
    X, y = [], []
    for _ in range(5):
        for i in range(9):
            X.append([float(i), float(i % 2)])
            y.append(0 if i <= 2 else (1 if i <= 5 else 2))
    return X, y


# ------------------------------------------------------- linear regression

class TestLinearRegression:
    def test_fits_line(self):
        X = [[float(i)] for i in range(10)]
        y = [2.0 * i + 1.0 for i in range(10)]
        model = LinearRegression().fit(X, y)
        preds = model.predict([[10.0], [11.0]])
        assert preds[0] == pytest.approx(21.0, abs=0.5)
        assert preds[1] == pytest.approx(23.0, abs=0.5)

    def test_r_squared_perfect_is_one(self):
        X = [[float(i)] for i in range(10)]
        y = [3.0 * i for i in range(10)]
        model = LinearRegression().fit(X, y)
        assert model.r_squared(X, y) == pytest.approx(1.0, abs=1e-6)

    def test_r_squared_not_clamped_negative(self):
        # Anti-correlated predictions must surface a negative R²,
        # never a hidden 0.0.
        y = [1.0, 2.0, 3.0, 4.0]
        assert r2_score(y, [4.0, 3.0, 2.0, 1.0]) < 0.0
        model = LinearRegression()
        model.coef_ = [-1.0]
        model.intercept_ = 0.0
        assert model.r_squared([[1.0], [2.0], [3.0], [4.0]], y) < 0.0

    def test_r_squared_constant_target_is_zero(self):
        model = LinearRegression().fit([[1.0], [2.0]], [5.0, 5.0])
        assert model.r_squared([[1.0]], [5.0]) == 0.0

    def test_mae(self):
        assert mean_absolute_error([1.0, 2.0], [1.5, 2.5]) == pytest.approx(0.5)

    def test_regression_scores_beats_baseline(self):
        X = [[float(i)] for i in range(20)]
        y = [2.0 * i for i in range(20)]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y)
        model = LinearRegression().fit(X_tr, y_tr)
        scores = regression_scores(y_te, model.predict(X_te))
        assert scores["r_squared"] > 0.9
        assert scores["mae"] < scores["baseline_mae"]

    def test_serialisation_round_trip(self):
        X = [[float(i)] for i in range(8)]
        y = [float(i) for i in range(8)]
        model = LinearRegression().fit(X, y)
        clone = LinearRegression.from_dict(model.to_dict())
        assert clone.predict(X) == pytest.approx(model.predict(X))


# --------------------------------------------------- tree / forest / knn

class TestDecisionTree:
    def test_binary_classification(self):
        X, y = binary_dataset()
        model = DecisionTreeClassifier(max_depth=4, seed=1).fit(X, y)
        assert model.predict([[1.0], [8.0]]) == [0, 1]

    def test_binary_predict_proba_contract(self):
        X, y = binary_dataset()
        model = DecisionTreeClassifier(max_depth=4, seed=1).fit(X, y)
        probas = model.predict_proba([[1.0], [8.0]])
        assert all(0.0 <= p <= 1.0 for p in probas)
        assert probas[0] < 0.5 < probas[1]

    def test_multiclass_predictions_cover_all_classes(self):
        X, y = multiclass_dataset()
        model = DecisionTreeClassifier(max_depth=6, seed=1).fit(X, y)
        preds = model.predict(X)
        assert set(preds) == {0, 1, 2}
        assert set(preds) != {0, 1}  # genuinely multiclass, not collapsed

    def test_multiclass_dist_sums_to_one(self):
        X, y = multiclass_dataset()
        model = DecisionTreeClassifier(max_depth=6, seed=1).fit(X, y)
        for dist in model.predict_dist(X[:5]):
            assert set(dist) == {0, 1, 2}
            assert sum(dist.values()) == pytest.approx(1.0)

    def test_feature_importances_normalised(self):
        X, y = multiclass_dataset()
        model = DecisionTreeClassifier(max_depth=6, seed=1).fit(X, y)
        assert len(model.feature_importances_) == 2
        assert sum(model.feature_importances_) == pytest.approx(1.0)
        assert model.feature_importances_[0] > model.feature_importances_[1]

    def test_rejects_empty_and_single_class(self):
        with pytest.raises(ValueError):
            DecisionTreeClassifier().fit([], [])
        with pytest.raises(ValueError):
            DecisionTreeClassifier().fit([[1.0], [2.0]], [0, 0])

    def test_constant_features_still_predicts(self):
        X = [[1.0, 1.0]] * 6 + [[1.0, 1.0]] * 6
        y = [0] * 6 + [1] * 6
        model = DecisionTreeClassifier(seed=1).fit(X, y)
        assert set(model.predict(X)) <= {0, 1}

    def test_serialisation_round_trip_multiclass(self):
        X, y = multiclass_dataset()
        model = DecisionTreeClassifier(max_depth=6, seed=1).fit(X, y)
        clone = DecisionTreeClassifier.from_dict(model.to_dict())
        assert clone.predict(X) == model.predict(X)
        assert clone.classes_ == [0, 1, 2]

    def test_legacy_artefact_loads(self):
        X, y = binary_dataset()
        model = DecisionTreeClassifier(max_depth=3, seed=1).fit(X, y)
        payload = model.to_dict()
        del payload["classes"]  # simulate a pre-multiclass artefact
        clone = DecisionTreeClassifier.from_dict(payload)
        assert clone.predict([[1.0], [8.0]]) == [0, 1]


class TestRandomForest:
    def test_binary_classification(self):
        X, y = binary_dataset()
        model = RandomForestClassifier(n_estimators=5, max_depth=4, seed=1).fit(X, y)
        assert model.predict([[1.0], [8.0]]) == [0, 1]

    def test_multiclass_majority_vote(self):
        X, y = multiclass_dataset()
        model = RandomForestClassifier(n_estimators=9, max_depth=6, seed=1).fit(X, y)
        preds = model.predict(X)
        assert set(preds) == {0, 1, 2}
        scores = classification_scores(y, preds)
        assert scores["accuracy"] > 0.85

    def test_importances_exposed(self):
        X, y = multiclass_dataset()
        model = RandomForestClassifier(n_estimators=5, max_depth=6, seed=1).fit(X, y)
        assert len(model.feature_importances_) == 2
        assert sum(model.feature_importances_) == pytest.approx(1.0, abs=1e-6)

    def test_rejects_empty_and_single_class(self):
        with pytest.raises(ValueError):
            RandomForestClassifier().fit([], [])
        with pytest.raises(ValueError):
            RandomForestClassifier().fit([[1.0]], [1])

    def test_serialisation_round_trip(self):
        X, y = binary_dataset()
        model = RandomForestClassifier(n_estimators=5, max_depth=4, seed=1).fit(X, y)
        clone = RandomForestClassifier.from_dict(model.to_dict())
        assert clone.predict(X) == model.predict(X)


class TestKNN:
    def test_binary_classification(self):
        X, y = binary_dataset()
        model = KNNClassifier(k=3).fit(X, y)
        assert model.predict([[0.5], [9.5]]) == [0, 1]

    def test_multiclass_majority_vote(self):
        X, y = multiclass_dataset()
        model = KNNClassifier(k=5).fit(X, y)
        preds = model.predict([[0.0, 0.0], [4.0, 0.0], [8.0, 0.0]])
        assert preds == [0, 1, 2]

    def test_rejects_empty_and_single_class(self):
        with pytest.raises(ValueError):
            KNNClassifier().fit([], [])
        with pytest.raises(ValueError):
            KNNClassifier().fit([[1.0]], [0])

    def test_serialisation_round_trip(self):
        X, y = multiclass_dataset()
        model = KNNClassifier(k=3).fit(X, y)
        clone = KNNClassifier.from_dict(model.to_dict())
        assert clone.predict(X[:10]) == model.predict(X[:10])


# ------------------------------------------------------------- evaluation

class TestEvaluation:
    def test_binary_confusion_matrix_legacy_shape(self):
        cm = confusion_matrix([0, 0, 1, 1], [0, 1, 0, 1])
        assert cm == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}

    def test_multiclass_confusion_matrix_n_class(self):
        cm = confusion_matrix([0, 1, 2, 2], [0, 2, 2, 1])
        assert cm["labels"] == [0, 1, 2]
        assert cm["matrix"] == [[1, 0, 0], [0, 0, 1], [0, 1, 1]]
        assert cm["support"] == 4

    def test_multiclass_helper_always_n_class(self):
        cm = confusion_matrix_multiclass([0, 1], [0, 1])
        assert cm["labels"] == [0, 1]
        assert cm["matrix"] == [[1, 0], [0, 1]]

    def test_binary_scores(self):
        scores = classification_scores([0, 0, 1, 1], [0, 1, 0, 1])
        assert scores["accuracy"] == pytest.approx(0.5)
        assert scores["precision"] == pytest.approx(0.5)
        assert scores["recall"] == pytest.approx(0.5)
        assert scores["f1"] == pytest.approx(0.5)

    def test_multiclass_scores_macro(self):
        y_true = [0, 0, 1, 1, 2, 2]
        y_pred = [0, 0, 1, 2, 2, 2]
        scores = classification_scores(y_true, y_pred)
        assert scores["num_classes"] == 3
        assert scores["averaging"] == "macro"
        assert scores["accuracy"] == pytest.approx(5 / 6)
        assert 0.0 <= scores["f1"] <= 1.0
        assert set(scores["per_class"]) == {"0", "1", "2"}

    def test_perfect_multiclass_scores_are_one(self):
        y = [0, 1, 2, 0, 1, 2]
        scores = classification_scores(y, list(y))
        assert scores["accuracy"] == pytest.approx(1.0)
        assert scores["f1"] == pytest.approx(1.0)

    def test_compare_models_multiclass(self):
        X, y = multiclass_dataset()
        tree = DecisionTreeClassifier(max_depth=6, seed=1).fit(X, y)
        knn = KNNClassifier(k=5).fit(X, y)
        table = evaluate.compare_models({"tree": tree, "knn": knn}, X, y)
        assert set(table) == {"tree", "knn"}
        assert table["tree"]["num_classes"] == 3

    def test_permutation_importance_ranks_signal(self):
        X = [[float(i), 0.0 if i % 2 == 0 else 1.0] for i in range(40)]
        y = [0 if i < 20 else 1 for i in range(40)]
        model = DecisionTreeClassifier(max_depth=4, seed=1).fit(X, y)
        ranked = evaluate.permutation_importance(model, X, y, ["signal", "noise"])
        assert ranked[0]["feature"] == "signal"


# ---------------------------------------------------------- preprocessing

class TestPreprocessing:
    def test_scaler_zero_mean_unit_variance(self):
        X = [[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]]
        scaler = StandardScaler().fit(X)
        out = scaler.transform(X)
        assert sum(r[0] for r in out) == pytest.approx(0.0, abs=1e-9)
        var = sum(r[0] ** 2 for r in out) / len(out)
        assert var == pytest.approx(1.0)

    def test_scaler_constant_column_safe(self):
        X = [[5.0, 1.0], [5.0, 2.0], [5.0, 3.0]]
        out = StandardScaler().fit_transform(X)
        assert all(r[0] == pytest.approx(0.0) for r in out)
        assert all(math.isfinite(v) for r in out for v in r)

    def test_scaler_round_trip(self):
        X = [[1.0], [2.0], [3.0]]
        scaler = StandardScaler().fit(X)
        clone = StandardScaler.from_dict(scaler.to_dict())
        expected = scaler.transform(X)
        actual = clone.transform(X)
        assert [r[0] for r in actual] == pytest.approx([r[0] for r in expected])

    def test_stratified_split_preserves_classes(self):
        X = [[float(i)] for i in range(30)]
        y = [0] * 15 + [1] * 15
        X_tr, X_te, y_tr, y_te = stratified_split(X, y, test_size=0.2)
        assert set(y_tr) == set(y_te) == {0, 1}
        assert len(X_tr) + len(X_te) == 30

    def test_stratified_split_multiclass(self):
        X = [[float(i)] for i in range(30)]
        y = [0] * 10 + [1] * 10 + [2] * 10
        _, _, y_tr, y_te = stratified_split(X, y, test_size=0.2)
        assert set(y_te) == {0, 1, 2}

    def test_train_test_split_rejects_empty(self):
        with pytest.raises(ValueError):
            train_test_split([], [])
        with pytest.raises(ValueError):
            train_test_split([[1.0]], [1.0])

    def test_train_test_split_both_sides_nonempty(self):
        X = [[float(i)] for i in range(10)]
        y = [float(i) for i in range(10)]
        X_tr, X_te, _, _ = train_test_split(X, y)
        assert len(X_tr) > 0 and len(X_te) > 0
        assert len(X_tr) + len(X_te) == 10


# ------------------------------------------------------------ recommender

class TestRecommender:
    def test_jaccard_edge_cases(self):
        assert jaccard(set(), set()) == 0.0
        assert jaccard({1, 2}, {1, 2}) == pytest.approx(1.0)
        assert jaccard({1}, {2}) == pytest.approx(0.0)

    def test_affinity_matrix_symmetric(self):
        tool_users = {"a": {1, 2, 3}, "b": {2, 3, 4}}
        tools, matrix = affinity_matrix(tool_users)
        assert tools == ["a", "b"]
        assert matrix[0][1] == pytest.approx(matrix[1][0])
        assert matrix[0][1] == pytest.approx(0.5)

    def test_kmeans_separates_clusters(self):
        rows = [[0.0, 0.0]] * 5 + [[10.0, 10.0]] * 5
        labels = kmeans(rows, k=2, seed=1)
        assert len(set(labels[:5])) == 1
        assert len(set(labels[5:])) == 1
        assert labels[0] != labels[5]

    def test_kmeans_empty_and_deterministic(self):
        assert kmeans([], k=3) == []
        rows = [[float(i)] for i in range(6)]
        assert kmeans(rows, k=2, seed=7) == kmeans(rows, k=2, seed=7)

    def test_recommend_filters_weak_scores(self):
        tools = ["a", "b", "c"]
        matrix = [[0.0, 0.03, 0.9], [0.03, 0.0, 0.04], [0.9, 0.04, 0.0]]
        labels = [0, 0, 0]
        assert recommend(tools, matrix, labels, min_score=0.05)["a"] == [
            ("c", 0.9, 0)
        ]
        # Legacy default keeps any positive pair.
        assert len(recommend(tools, matrix, labels)["a"]) == 2

    def test_recommendation_reason_mentions_tools(self):
        text = recommendation_reason("bg-remove", "upscale", 0.42)
        assert "bg-remove" in text and "upscale" in text


# ------------------------------------------------- missing-value handling

class TestMissingValues:
    def test_csvkit_profiles_missing(self):
        from apps.data_science.csvkit import profile_dataset

        header = ["age", "city"]
        rows = [["25", ""], ["", "paris"], ["30", "paris"]]
        profile = profile_dataset(header, rows)
        by_name = {c["name"]: c for c in profile["columns"]}
        assert by_name["age"]["missing"] == 1
        assert by_name["city"]["missing"] == 1

    def test_csvkit_cleans_missing_to_ml_ready_floats(self):
        from apps.data_science.csvkit import clean_dataset

        header = ["age", "city", "label"]
        rows = [["25", "", "0"], ["", "paris", "1"], ["30", "paris", "0"]]
        out_header, out_rows, _report = clean_dataset(
            header, rows, {"target": "label"}
        )
        assert all(
            all(isinstance(v, float) for v in row) for row in out_rows
        )
        assert len(out_rows) == 3
