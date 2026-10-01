"""Reusable FMU build helpers backed by OpenModelica's ``omc`` CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess


@dataclass(frozen=True)
class BuildRequest:
    """Configuration for exporting a single Modelica class as an FMU."""

    model_name: str
    output_dir: Path
    load_files: tuple[Path, ...] = ()
    omc_path: str = "omc"
    working_dir: Path = Path.cwd()
    fmi_version: str = "2.0"
    fmu_type: str = "cs"
    platforms: tuple[str, ...] = ("static",)
    fmi_flags: tuple[str, ...] = ()
    runtime_depends: str | None = "all"
    modelica_version: str | None = None
    output_name: str | None = None
    dry_run: bool = False

    @property
    def target_path(self) -> Path:
        name = self.output_name or f"{self.model_name.replace('.', '_')}.fmu"
        return self.output_dir / name

    @property
    def mos_path(self) -> Path:
        return self.target_path.with_suffix(".mos")


@dataclass(frozen=True)
class BuildResult:
    """Outcome for one FMU build request."""

    request: BuildRequest
    built_path: Path | None
    target_path: Path
    stdout: str
    stderr: str


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _mos_string(value: str | Path) -> str:
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_mos_script(request: BuildRequest) -> str:
    lines: list[str] = []

    if request.modelica_version:
        lines.append(
            f"installPackage(Modelica, {_mos_string(request.modelica_version)}, exactMatch=false);"
        )

    for load_file in request.load_files:
        lines.append(f"loadFile({_mos_string(load_file)});")

    lines.append(f"cd({_mos_string(request.output_dir)});")

    for fmi_flag in request.fmi_flags:
        lines.append(f"setCommandLineOptions({_mos_string(f'--fmiFlags={fmi_flag}')});")

    if request.runtime_depends:
        lines.append(
            f"setCommandLineOptions({_mos_string(f'--fmuRuntimeDepends={request.runtime_depends}')});"
        )

    platforms = ", ".join(_mos_string(platform) for platform in request.platforms)
    lines.append(
        "filename := OpenModelica.Scripting.buildModelFMU("
        f"{request.model_name}, version={_mos_string(request.fmi_version)}, "
        f"fmuType={_mos_string(request.fmu_type)}, platforms={{{platforms}}});"
    )
    lines.append("filename;")
    lines.append("getErrorString();")
    return "\n".join(lines) + "\n"


def run_omc(
    omc_path: str,
    mos_content: str,
    mos_path: Path,
    working_dir: Path,
    dry_run: bool = False,
) -> tuple[str, str]:
    ensure_directory(mos_path.parent)
    mos_path.write_text(mos_content, encoding="utf-8")

    if dry_run:
        print(f"[dry-run] Wrote omc script to {mos_path}")
        return "", ""

    try:
        proc = subprocess.run(
            [omc_path, str(mos_path)],
            check=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            "omc executable not found. Install OpenModelica or pass --omc-path."
        ) from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise SystemExit(message) from exc

    return proc.stdout, proc.stderr


def extract_fmu_path(output: str, output_dir: Path) -> Path | None:
    matches = re.findall(r"\"([^\"]+\.fmu)\"", output)
    if not matches:
        return None

    candidate = Path(matches[-1])
    if candidate.is_absolute():
        return candidate
    return output_dir / candidate


def build_fmus(
    requests: list[BuildRequest],
    clean_output_dir: bool = False,
) -> list[BuildResult]:
    results: list[BuildResult] = []
    cleaned_dirs: set[Path] = set()

    for request in requests:
        if clean_output_dir and request.output_dir not in cleaned_dirs and request.output_dir.exists():
            shutil.rmtree(request.output_dir)
            cleaned_dirs.add(request.output_dir)

        ensure_directory(request.output_dir)

        stdout, stderr = run_omc(
            omc_path=request.omc_path,
            mos_content=build_mos_script(request),
            mos_path=request.mos_path,
            working_dir=request.working_dir,
            dry_run=request.dry_run,
        )

        built_path: Path | None = None
        if not request.dry_run:
            built_path = extract_fmu_path(stdout, request.output_dir)
            if not built_path:
                raise SystemExit(
                    f"Could not locate FMU emitted for {request.model_name}. omc output: {stdout}"
                )

            if not built_path.exists():
                raise SystemExit(
                    f"FMU file {built_path} missing after omc run for {request.model_name}."
                )

            if built_path.resolve() != request.target_path.resolve():
                request.target_path.unlink(missing_ok=True)
                shutil.move(str(built_path), request.target_path)
            built_path = request.target_path

        results.append(
            BuildResult(
                request=request,
                built_path=built_path,
                target_path=request.target_path,
                stdout=stdout,
                stderr=stderr,
            )
        )

    return results
