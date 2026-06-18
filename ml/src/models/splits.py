"""
Grouped train/test split and CV splitter.

Both augmented rows of a match (ally=Blue / ally=Red) share a match_id and
must land in the same fold — otherwise the model can "see the answer" via
its mirror row in another split.
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import RANDOM_SEED


def train_test_split_grouped(df: pd.DataFrame, test_size: float = 0.15):
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=RANDOM_SEED)
    train_idx, test_idx = next(splitter.split(df, df["ally_win"], groups=df["match_id"]))
    return df.iloc[train_idx].reset_index(drop=True), df.iloc[test_idx].reset_index(drop=True)


def cv_splitter(n_splits: int = 5):
    return StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_SEED)
