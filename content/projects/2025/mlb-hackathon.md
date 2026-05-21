---
title: "MLB Hall of Fame Predictor"
date: 2025-01-17
description: "A scikit-learn decision tree that guesses whether a current MLB player would get voted into Cooperstown, built for the Google Cloud x MLB hackathon."
tags: ["AI", "Python", "Hackathon", "AI-written"]
categories: ["Projects"]
draft: false
image: "/previews/default-project.png"
---

This was my entry for the Google Cloud x MLB hackathon back in December. The prompt was open-ended around baseball data, and I picked the Hall of Fame angle because the question is fun to argue about and the dataset is actually clean enough to model without spending the whole weekend on data prep.

The data is the Lahman Baseball Database (1871-2023) — every player, every season, batting/pitching/fielding splits, awards, and the Hall of Fame ballot history. The pitch was: take a current player's career-to-date stats, feed them into a model trained on the historical record of who got inducted and who didn't, and get a probability back. Are we looking at a future Hall of Famer or a regular?

Most of the actual hackathon time was spent in `merging.py`. Lahman ships as a dozen separate CSVs that you have to aggregate per-player and then join — sum every season of batting into a career line, do the same for pitching and fielding, count awards per player, then left-join the Hall of Fame ballot table to get the `inducted` label. There's a lot of room here to be clever (era adjustments, advanced metrics, position weighting) and I did none of it. Hackathon scope.

The features I ended up training on are mostly the obvious counting stats — games, at-bats, runs, hits, doubles, triples, home runs, RBIs, walks, strikeouts on the batting side; wins, losses, ERA, saves, K's on the pitching side; putouts, assists, errors on the fielding side; plus an `AwardsCount` column I built by aggregating `AwardsPlayers.csv`. Twenty-three features total, all numeric.

```python
feature_columns = [
    'BattingGames', 'AtBats', 'Runs', 'Hits', 'Doubles', 'Triples', 'HomeRuns', 'RBIs', 'Walks', 'Strikeouts',
    'Wins', 'Losses', 'PitchingGames', 'GamesStarted', 'CompleteGames', 'Saves', 'PitchingStrikeouts', 'EarnedRunAverage',
    'FieldingGames', 'Putouts', 'Assists', 'Errors', 'AwardsCount'
]

features = data[feature_columns]
labels = data['inducted']

train_features, test_features, train_labels, test_labels = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

skmodel = DecisionTreeClassifier()
skmodel.fit(train_features, train_labels)
print('accuracy is:', skmodel.score(test_features, test_labels))
```

The model is a vanilla scikit-learn `DecisionTreeClassifier` — no tuning, no ensemble, no cross-validation beyond a single 80/20 split. The class imbalance is real: a tiny fraction of MLB players ever make the Hall, so raw accuracy is a misleading number to chase. A "predict not inducted for everyone" baseline already gets you into the high 90s. I'd want to look at precision/recall on the inducted class before claiming the model is actually doing anything, and a fair-weekend version of this would swap in a random forest or gradient boosting with proper stratified CV.

The cloud half of the project is in `interact.py` and a Vertex AI endpoint — `train.py` has the commented-out GCS upload, the idea being you'd push `model.joblib` to a bucket, deploy it to Vertex, and hit it from anywhere with a prediction call. I had the wiring in place but ran out of time to actually deploy the endpoint before the deadline, so the production-y version is more of a sketch.

Things I'd do with another weekend on this: real per-season time-series instead of career totals (the dataset is called `_Timeseries` for a reason but I collapsed it), position-aware features, era adjustments so a 1920s slugger doesn't get penalized for not having modern counting stats, and an actual frontend where you pick a current player and get a probability back. Also, evaluating against players who recently became eligible but aren't inducted yet would be a more honest test than a random split.

[GitHub Repo](https://github.com/EricSpencer00/MLB-Hackathon)

---

*Written with AI.*
