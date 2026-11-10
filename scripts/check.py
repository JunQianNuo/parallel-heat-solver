"""Run CTest and display measured test durations to four decimal places."""
import argparse
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test-dir', type=Path, default=Path('build'))
    parser.add_argument('--ctest', default='ctest')
    args = parser.parse_args()
    directory = args.test_dir.resolve()
    if not directory.is_dir():
        parser.error(f'build directory does not exist: {directory}')
    start = time.perf_counter()
    result = subprocess.run(
        [args.ctest, '--test-dir', str(directory), '-T', 'Test', '--output-on-failure'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    elapsed = time.perf_counter() - start
    raw_log = directory / 'ctest-raw.log'
    raw_log.write_text(result.stdout)
    if result.returncode:
        print(result.stdout, end='')
        return result.returncode if result.returncode > 0 else 1
    # Dashboard XML has unrounded Execution Time measurements, unlike the
    # two-decimal console output. -T Test only runs tests; it submits nothing.
    try:
        tag = (directory / 'Testing' / 'TAG').read_text().splitlines()[0]
        report = directory / 'Testing' / tag / 'Test.xml'
        tests = ET.parse(report).findall('./Testing/Test')
        if not tests:
            raise ValueError('CTest reported no tests')
        print('CTest results (seconds, 4 decimal places):')
        for index, test in enumerate(tests, 1):
            name = test.findtext('Name')
            duration = float(test.findtext(
                "./Results/NamedMeasurement[@name='Execution Time']/Value"))
            status = test.attrib['Status']
            print(f'{index}/{len(tests)} {name:<24} {status:<8} {duration:.4f} sec')
        print(f'CTest invocation wall time: {elapsed:.4f} sec')
        print(f'Raw CTest output: {raw_log}')
        print(f'Unrounded test measurements: {report}')
        return 0
    except (OSError, ET.ParseError, ValueError, TypeError, KeyError, IndexError) as error:
        print(result.stdout, end='')
        print(f'Cannot read CTest timing results: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
