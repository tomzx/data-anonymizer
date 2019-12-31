from argparse import ArgumentParser

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OrdinalEncoder, Binarizer


def run():
    argument_parser = ArgumentParser()
    argument_parser.add_argument("file", help="Path to data file")
    argument_parser.add_argument(
        "output", help="Path where to store the anonymized data"
    )
    argument_parser.add_argument(
        "--feature-anonymize", nargs="+", help="Remove feature name (* to anonymize all)"
    )
    argument_parser.add_argument(
        "--feature-binarize", nargs="+", help="Feature to binarize (either 0 or 1)"
    )
    argument_parser.add_argument(
        "--feature-clamp",
        nargs="+",
        default=[],
        help="Feature is limited between min/max (last 2 values)",
    )
    argument_parser.add_argument(
        "--feature-categorize", nargs="+", help="Categorical feature to anonymize"
    )
    argument_parser.add_argument(
        "--feature-fill",
        nargs="+",
        default=[],
        help="Feature is replaced by fill value (last provided value)",
    )
    argument_parser.add_argument(
        "--feature-min-max-scale",
        nargs="+",
        default=[],
        help="Feature to scale between 0 and 1",
    )
    argument_parser.add_argument(
        "--feature-remove", nargs="+", help="Feature to remove"
    )
    argument_parser.add_argument(
        "--feature-round",
        nargs="+",
        default=[],
        help="Round feature to closest multiple (last provided value)",
    )

    args = argument_parser.parse_args()

    df = pd.read_csv(args.file, comment="#")

    transforms = []

    # Remove features
    if args.feature_remove:
        df = df.drop(columns=args.feature_remove)

    # Scale features between 0 and 1
    min_max_scaler = MinMaxScaler()

    if args.feature_min_max_scale:
        min_max_scaler.fit(df[args.feature_min_max_scale])

        df[args.feature_min_max_scale] = min_max_scaler.transform(
            df[args.feature_min_max_scale]
        )

        transforms += [f"feature-min-max-scale {' '.join(args.feature_min_max_scale)}"]

    # Binarize
    binarizer = Binarizer(threshold=0.5)

    if args.feature_binarize:
        min_max_scaler.fit(df[args.feature_binarize])

        df[args.feature_binarize] = min_max_scaler.transform(df[args.feature_binarize])

        df[args.feature_binarize] = binarizer.transform(df[args.feature_binarize])

        transforms += [f"feature-binarize {' '.join(args.feature_binarize)}"]

    # Categorize
    ordinal_encoder = OrdinalEncoder(dtype=np.int)

    if args.feature_categorize:
        ordinal_encoder.fit(df[args.feature_categorize])

        # Replace categorical columns by letters
        df[args.feature_categorize] = ordinal_encoder.transform(
            df[args.feature_categorize]
        )
        # Prefix with C to indicate it's a categorical
        df[args.feature_categorize] = "C" + df[args.feature_categorize].astype(str)

        transforms += [f"feature-categorize {' '.join(args.feature_categorize)}"]

    # Fill
    # TODO: Support different fill per column
    if len(args.feature_fill) > 1:
        df[args.feature_fill[:-1]] = args.feature_fill[-1]

        transforms += [f"feature-fill {' '.join(args.feature_fill)}"]

    # Clamp
    # TODO: Support different clamp min/max per column
    if len(args.feature_clamp) > 2:
        features = args.feature_clamp[:-2]
        minimum = float(args.feature_clamp[-2])
        df[features] = df[features].where(df[features] >= minimum, other=minimum)

        maximum = float(args.feature_clamp[-1])
        df[features] = df[features].where(df[features] <= maximum, other=maximum)

        transforms += [f"feature-clamp {' '.join(args.feature_clamp)}"]

    # Round
    if len(args.feature_round) > 1:
        multiple = float(args.feature_round[-1])
        df[args.feature_round[:-1]] = (
            round(df[args.feature_round[:-1]] / multiple) * multiple
        )

        transforms += [f"feature-round {' '.join(args.feature_round)}"]

    # TODO: Use the robust scaler to ignore outliers

    # Anonymize list of features
    if args.feature_anonymize:
        if "*" in args.feature_anonymize:
            features_anonymize = df.columns
        else:
            features_anonymize = args.feature_anonymize

        mapping = {feature: i for i, feature in enumerate(features_anonymize)}

        df = df.rename(columns=mapping)

        for i, transform in enumerate(transforms):
            # Add a space at the end so we can match the last input
            transform += " "
            for key, value in mapping.items():
                transform = transform.replace(f" {key} ", f" {value} ")

            transforms[i] = transform

    with open(args.output, "w") as f:
        for transform in transforms:
            f.write("# " + transform + "\n")
        df.to_csv(f, index=False, line_terminator="\n")

    # TODO: Generate a mapping so that having the initial data allows you to understand
    # someone referring to the transformed data
