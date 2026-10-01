"""CLI for exporting one or many Modelica models as FMUs."""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import BuildRequest, build_fmus


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        dest="models",
        action="append",
        required=True,
        help="Fully qualified Modelica class to export. Repeat for multiple FMUs.",
    )
    parser.add_argument(
        "--load-file",
        action="append",
        default=[],
        type=Path,
        help="Modelica file or package.mo to load before building. Repeat as needed.",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("build/fmus"),
        type=Path,
        help="Directory where generated FMUs are written.",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        help="Explicit FMU filename. Only valid when building a single model.",
    )
    parser.add_argument(
        "--omc-path",
        default="omc",
        help="Path to the OpenModelica omc executable.",
    )
    parser.add_argument(
        "--working-dir",
        default=Path.cwd(),
        type=Path,
        help="Working directory used when invoking omc.",
    )
    parser.add_argument(
        "--fmi-version",
        default="2.0",
        help="FMI version passed to buildModelFMU.",
    )
    parser.add_argument(
        "--fmu-type",
        choices=("cs", "me"),
        default="cs",
        help="FMU type passed to buildModelFMU.",
    )
    parser.add_argument(
        "--platform",
        dest="platforms",
        action="append",
        default=["static"],
        help="Target platform passed to buildModelFMU. Repeat for multiple platforms.",
    )
    parser.add_argument(
        "--fmi-flag",
        dest="fmi_flags",
        action="append",
        default=["s:cvode"],
        help="Value forwarded to --fmiFlags. Repeat to provide multiple flags.",
    )
    parser.add_argument(
        "--runtime-depends",
        default="all",
        help="Value forwarded to --fmuRuntimeDepends. Use 'none' or an empty string to disable.",
    )
    parser.add_argument(
        "--modelica-version",
        default="4.0.0",
        help="Optional Modelica standard library version installed via installPackage(Modelica, ...).",
    )
    parser.add_argument(
        "--clean-output-dir",
        action="store_true",
        help="Remove the output directory before building.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated omc scripts without invoking omc.",
    )
    return parser.parse_args()


def _normalize_runtime_depends(value: str) -> str | None:
    stripped = value.strip()
    if not stripped or stripped.lower() == "none":
        return None
    return stripped


def build_requests(args: argparse.Namespace) -> list[BuildRequest]:
    if args.output_name and len(args.models) != 1:
        raise SystemExit("--output-name can only be used when building a single model.")

    platforms = tuple(args.platforms)
    runtime_depends = _normalize_runtime_depends(args.runtime_depends)
    load_files = tuple(path.resolve() for path in args.load_file)
    output_dir = args.output_dir.resolve()
    working_dir = args.working_dir.resolve()

    return [
        BuildRequest(
            model_name=model,
            output_dir=output_dir,
            load_files=load_files,
            omc_path=args.omc_path,
            working_dir=working_dir,
            fmi_version=args.fmi_version,
            fmu_type=args.fmu_type,
            platforms=platforms,
            fmi_flags=tuple(args.fmi_flags),
            runtime_depends=runtime_depends,
            modelica_version=args.modelica_version,
            output_name=args.output_name if len(args.models) == 1 else None,
            dry_run=args.dry_run,
        )
        for model in args.models
    ]


def main() -> int:
    args = parse_args()
    requests = build_requests(args)

    for request in requests:
        print(f"Exporting {request.model_name} -> {request.target_path}")

    results = build_fmus(requests, clean_output_dir=args.clean_output_dir)

    for result in results:
        if result.stderr.strip():
            print(result.stderr.strip())
        if not result.request.dry_run:
            print(f"  -> {result.target_path}")

    print("FMU build process finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
