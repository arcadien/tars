"""Requirement coverage: every validated requirement is checked somewhere, or justified in audits/exclusions.yml.

Covered = a pytest test tagged @pytest.mark.req('<ID>'), a manual test sheet tests/bench/<ID>.md or
tests/manual/<ID>.md, or a firmware Unity test tagged `// req: <ID>` under software/. A requirement whose acceptance
needs the firmware (Unity, on-target) is only reported (warning) while no firmware test exists yet; it becomes
mandatory with the first one. A manual sheet that was never run (no result line) is reported too.
"""
import glob
import os
import re
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = r'[A-Z]+-[A-Z0-9]+-[A-Z0-9]+-\d{3}'
SECTIONS = ('## Equipment', '## Setup', '## Steps', '## Pass criteria', '## Results')


def read(path):
    return open(path, encoding='utf-8').read()


def requirements():
    """{id: (status, acceptance text)}"""
    reqs = {}
    for f in glob.glob(os.path.join(ROOT, 'requirements', '*.md')):
        for m in re.finditer(rf'^### ({ID})\n(?:\*\*.*\n)*?\*\*Status:\*\* (\S+)\n(?:.*\n)*?\*\*Description:\*\* (.*)',
                             read(f), re.M):
            reqs[m.group(1)] = (m.group(2), m.group(3).split('Acceptance', 1)[-1])
    return reqs


def sheets():
    return glob.glob(os.path.join(ROOT, 'tests', 'bench', '*-*-*-*.md')) + \
        glob.glob(os.path.join(ROOT, 'tests', 'manual', '*-*-*-*.md'))


def unity_tagged():
    files = [f for ext in ('c', 'cpp', 'h') for f in glob.glob(os.path.join(ROOT, 'software', '**', f'*.{ext}'),
                                                                 recursive=True)]
    return {i for f in files for i in re.findall(rf'// req: ({ID})', read(f))}


def test_every_validated_requirement_is_tested_or_excluded():
    # Given the validated requirements, the tests, the test sheets and the exclusions
    reqs = {i: acc for i, (st, acc) in requirements().items() if st == 'validated'}
    tagged = {i for f in glob.glob(os.path.join(ROOT, 'tests', '*.py'))
              for i in re.findall(rf"@pytest\.mark\.req\('({ID})'\)", read(f))}
    unity = unity_tagged()
    covered = tagged | {os.path.basename(f)[:-3] for f in sheets()} | unity
    excluded = set(re.findall(ID, read(os.path.join(ROOT, 'audits', 'exclusions.yml'))))
    # When the firmware has no test yet, its requirements are pending, not missing
    pending = sorted(i for i, acc in reqs.items() if i not in covered | excluded and not unity
                     and re.search(r'Unity|on-target|firmware', acc))
    if pending:
        warnings.warn(f'{len(pending)} requirement(s) wait for firmware tests: {", ".join(pending)}')
    # Then every other validated requirement is covered or excluded
    assert sorted(set(reqs) - covered - excluded - set(pending)) == []


def test_every_test_sheet_is_complete_and_names_a_requirement():
    reqs = requirements()
    never_run = []
    for f in sheets():
        rid, text = os.path.basename(f)[:-3], read(f)
        # Given a manual test sheet: it is named after an existing requirement and links to it
        assert rid in reqs, f'{f}: no requirement {rid}'
        assert f'[{rid}](../../requirements/' in text, f'{f}: no link to its requirement'
        # Then it has every section, in order
        pos = [text.find(s) for s in SECTIONS]
        assert -1 not in pos and pos == sorted(pos), f'{f}: sections missing or out of order'
        # And its result table has a header; a sheet without any result line was never run
        rows = [ln for ln in text[pos[-1]:].splitlines() if ln.startswith('|')]
        assert len(rows) >= 2 and rows[0].startswith('| Date |'), f'{f}: no result table'
        if len(rows) == 2:
            never_run.append(rid)
    if never_run:
        warnings.warn(f'{len(never_run)} manual test sheet(s) never run: {", ".join(sorted(never_run))}')
