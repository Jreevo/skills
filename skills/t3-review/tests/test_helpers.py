#!/usr/bin/env python3
"""Regression tests use synthetic evidence. No network or credentials."""
import contextlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


t = load('triage')
r = load('review_state')


def response(flags=(), work_type='code', size=0, effort=0):
    return {'answers': [{'name': name, 'type': 'predicate', 'probability': int(name in flags)} for name in t.PREDICATES] +
            [{'name': 'work_type', 'type': 'choice', 'choice': work_type},
             {'name': 'size', 'type': 'score', 'score': size}, {'name': 'effort', 'type': 'score', 'score': effort}]}


def record(**overrides):
    row = dict(date='2026-10-08', slug='test', workType='code', tier='Heavy', triageTier='Heavy', escalated=False,
               effort='high', seatEffort='high', model='test-model', provider='test-provider', lens='correctness',
               findings=2, confirmed=1, rejected=1, plausible=0, status='completed', runId='run1', taskId='task1',
               round=1, triageSource='manual', coverage='full')
    row.update(overrides)
    return row


class TriageTests(unittest.TestCase):
    def test_risk_categories_and_effort_floors(self):
        for flag in t.PREDICATES:
            with self.subTest(flag=flag):
                out = t.classify(response(flags=[flag]))
                critical = flag in {'irreversible', 'money_movement', 'security_boundary', 'legal'}
                self.assertEqual(out['tier'], 'Critical' if critical else 'Heavy')
                self.assertEqual(out['reviewers'], 4 if critical else 3)
                self.assertEqual(out['effort'], 'xhigh' if critical else 'high')

    def test_plan_and_mixed_have_standard_floor(self):
        for kind in ['plan', 'mixed']:
            self.assertEqual(t.classify(response(work_type=kind))['tier'], 'Standard')
        for kind in ['code', 'copy']:
            self.assertEqual(t.classify(response(work_type=kind))['tier'], 'Light')

    def test_large_work_gets_heavy_review(self):
        self.assertEqual(t.classify(response(size=2.75))['tier'], 'Heavy')

    def test_missing_refused_and_duplicate_are_rejected(self):
        cases = [{'answers': []}, {}, {'answers': None}]
        for name in [a['name'] for a in response()['answers']]:
            incomplete = response()
            incomplete['answers'] = [a for a in incomplete['answers'] if a['name'] != name]
            refused = response()
            for a in refused['answers']:
                if a['name'] == name:
                    a['type'] = 'refusal'
            duplicate = response()
            duplicate['answers'].append(next(dict(a) for a in duplicate['answers'] if a['name'] == name))
            cases.extend([incomplete, refused, duplicate])
        for evidence in cases:
            with self.subTest(evidence=evidence):
                with self.assertRaises(t.TriageError):
                    t.classify(evidence)

    def test_invalid_probabilities_and_scores_are_rejected(self):
        for value in [None, True, '0', -1, 1.1, math.nan, math.inf]:
            evidence = response()
            evidence['answers'][0]['probability'] = value
            with self.subTest(value=value), self.assertRaises(t.TriageError):
                t.classify(evidence)
        for name, value in [('size', 4.1), ('effort', 3.1), ('size', -0.1), ('effort', None), ('effort', False)]:
            evidence = response()
            for a in evidence['answers']:
                if a['name'] == name:
                    a['score'] = value
            with self.assertRaises(t.TriageError):
                t.classify(evidence)

    def test_unknown_names_types_and_choice_are_rejected(self):
        evidence = response()
        evidence['answers'].append({'name': 'unexpected', 'type': 'predicate', 'probability': 0})
        with self.assertRaises(t.TriageError):
            t.classify(evidence)
        evidence = response(work_type='other')
        with self.assertRaises(t.TriageError):
            t.classify(evidence)
        evidence = response()
        evidence['answers'][0]['type'] = 'score'
        with self.assertRaises(t.TriageError):
            t.classify(evidence)

    def test_oversized_input_does_not_read_key_or_call_api(self):
        with patch.object(t, 'api_key') as key, patch.object(t.urllib.request, 'urlopen') as request:
            with self.assertRaises(t.TriageError):
                t.decide('a' * t.MAX_INPUT_CHARS + 'dangerous tail')
            key.assert_not_called()
            request.assert_not_called()

    def test_maximum_input_is_sent_whole(self):
        text = 'a' * (t.MAX_INPUT_CHARS - 4) + 'TAIL'
        reply = io.StringIO(json.dumps(response()))
        with patch.object(t, 'api_key', return_value='synthetic'), patch.object(t.urllib.request, 'urlopen', return_value=reply) as request:
            t.decide(text)
            sent = json.loads(request.call_args.args[0].data)
            self.assertEqual(sent['input'], text)

    def test_empty_key_rejected(self):
        with patch.object(t.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout=' \n')):
            with self.assertRaises(t.TriageError):
                t.api_key()

    def test_manual_cli_and_invalid_cli_exit(self):
        with tempfile.TemporaryDirectory() as d:
            packet = Path(d) / 'packet.md'
            packet.write_text('Complete refund execution plan')
            evidence = Path(d) / 'answers.json'
            evidence.write_text(json.dumps(response(flags=['money_movement'], work_type='plan')))
            cmd = [sys.executable, '-I', str(ROOT / 'triage.py'), str(packet), '--manual', str(evidence)]
            good = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(good.returncode, 0, good.stderr)
            out = json.loads(good.stdout)
            self.assertEqual((out['tier'], out['source'], out['cost_usd']), ('Critical', 'manual', None))
            evidence.write_text('{"answers": []}')
            bad = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1)
            self.assertEqual(bad.stdout, '')

    def test_policy_does_not_need_a_packet_or_key(self):
        result = subprocess.run([sys.executable, '-I', str(ROOT / 'triage.py'), '--policy'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        policy = json.loads(result.stdout)
        self.assertIn('money_movement', policy['critical'])
        self.assertEqual(t.classify(policy['answer_format'])['tier'], 'Light')


class StateTests(unittest.TestCase):
    def test_unique_private_snapshots_preserve_original(self):
        with tempfile.TemporaryDirectory() as d:
            packet = Path(d) / 'draft.md'
            packet.write_text('Original review target')
            first = r.prepare(packet, ['claude:author'], 'codex:chair', 600)
            packet.write_text('Changed target')
            second = r.prepare(packet, ['claude:author'], 'codex:chair', 600)
            self.addCleanup(lambda: __import__('shutil').rmtree(Path(first['statePath']).parent))
            self.addCleanup(lambda: __import__('shutil').rmtree(Path(second['statePath']).parent))
            self.assertNotEqual(first['runId'], second['runId'])
            self.assertNotEqual(first['packetSha256'], second['packetSha256'])
            self.assertEqual(Path(first['packetPath']).read_text(), 'Original review target')
            self.assertEqual(Path(first['packetPath']).stat().st_mode & 0o777, 0o600)
            self.assertEqual(Path(first['statePath']).stat().st_mode & 0o777, 0o600)
            self.assertEqual(Path(first['statePath']).parent.stat().st_mode & 0o777, 0o700)

    def test_invalid_timeout_rejected_before_directory_creation(self):
        with patch.object(r.tempfile, 'mkdtemp') as create:
            with self.assertRaises(ValueError):
                r.prepare('unused', ['unknown'], 'chair', 0)
            create.assert_not_called()

    def test_append_retry_does_not_duplicate_or_replace(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'scoreboard.jsonl'
            self.assertTrue(r.append_record(record(), path)['appended'])
            self.assertFalse(r.append_record(record(), path)['appended'])
            original = path.read_text()
            with self.assertRaises(ValueError):
                r.append_record(record(confirmed=2, rejected=0), path)
            self.assertEqual(path.read_text(), original)

    def test_invalid_record_does_not_mutate_history(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'scoreboard.jsonl'
            r.append_record(record(), path)
            original = path.read_text()
            with self.assertRaises(ValueError):
                r.append_record(record(taskId='new', confirmed=3), path)
            self.assertEqual(path.read_text(), original)

    def test_new_record_requires_complete_assessment_metadata(self):
        for field in ['round', 'triageSource', 'coverage', 'status', 'plausible']:
            row = record()
            del row[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.validate_record(row, new=True)
        with self.assertRaises(ValueError):
            r.validate_record(record(confirmed=0), new=True)

    def test_append_preserves_valid_final_line_without_newline(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'scoreboard.jsonl'
            path.write_text(json.dumps(record()))
            r.append_record(record(taskId='task2', runId='run2'), path)
            self.assertEqual(len([json.loads(line) for line in path.read_text().splitlines()]), 2)

    def test_failed_and_rebuttal_seats_do_not_inflate_ranking(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'scoreboard.jsonl'
            rows = [record(), record(taskId='round2', confirmed=2, rejected=0),
                    record(runId='run2', taskId='failed', status='failed', findings=None, confirmed=None, rejected=None, plausible=None)]
            path.write_text('\n'.join(json.dumps(row) for row in rows) + '\nmalformed\n')
            result = r.ranking('code', path)
            self.assertEqual(result['models'][0]['reviews'], 1)
            self.assertEqual(result['models'][0]['confirmed'], 1)
            self.assertEqual(result['skippedLines'], [4])

    def test_bad_history_is_preserved_and_disclosed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'scoreboard.jsonl'
            path.write_text('malformed\n')
            result = r.append_record(record(), path)
            self.assertEqual(result['skippedLines'], [1])
            self.assertTrue(path.read_text().startswith('malformed\n'))
            self.assertEqual(r.ranking('code', path)['skippedLines'], [1])


if __name__ == '__main__':
    unittest.main()
