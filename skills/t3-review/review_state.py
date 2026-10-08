#!/usr/bin/env python3
"""Private review packets and validated, idempotent scoreboard records (macOS)."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid
from datetime import datetime, timezone, date

SCOREBOARD = Path(__file__).with_name('scoreboard.jsonl')


def private_write(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        handle.write(text)


def prepare(packet, authors, chair, timeout_seconds):
    if not 1 <= timeout_seconds <= 3600:
        raise ValueError('timeout-seconds must be between 1 and 3600')
    if not authors or any(not isinstance(author, str) or not author.strip() for author in authors) or not isinstance(chair, str) or not chair.strip():
        raise ValueError('author and chair identities are required')
    text = Path(packet).read_text(encoding='utf-8')
    if not text.strip():
        raise ValueError('packet is empty')
    run_id = uuid.uuid4().hex
    directory = Path(tempfile.mkdtemp(prefix='t3-review-' + run_id + '-'))
    now = datetime.now(timezone.utc)
    state = {'runId': run_id, 'authors': authors, 'chair': chair,
             'packetPath': str(directory / 'packet.md'),
             'packetSha256': hashlib.sha256(text.encode()).hexdigest(),
             'createdAt': now.isoformat(), 'timeoutSeconds': timeout_seconds,
             'rounds': {}, 'tasks': []}
    private_write(directory / 'packet.md', text)
    private_write(directory / 'state.json', json.dumps(state, indent=2) + '\n')
    return dict(state, statePath=str(directory / 'state.json'))


def validate_record(row, new=False):
    if not isinstance(row, dict):
        raise ValueError('scoreboard record must be an object')
    required = ['date', 'slug', 'workType', 'tier', 'triageTier', 'escalated', 'effort',
                'seatEffort', 'model', 'provider', 'lens', 'findings', 'confirmed', 'rejected']
    if any(key not in row for key in required):
        raise ValueError('scoreboard record lacks required fields')
    for key in ['date', 'slug', 'seatEffort', 'model', 'provider', 'lens']:
        if not isinstance(row[key], str) or not row[key].strip():
            raise ValueError('invalid scoreboard field: ' + key)
    date.fromisoformat(row['date'])
    if row['workType'] not in ['code', 'plan', 'copy', 'mixed']:
        raise ValueError('invalid workType')
    if row['tier'] not in ['Light', 'Standard', 'Heavy', 'Critical'] or row['triageTier'] not in ['Light', 'Standard', 'Heavy', 'Critical']:
        raise ValueError('invalid tier')
    if type(row['escalated']) is not bool or row['effort'] not in ['medium', 'high', 'xhigh', 'max']:
        raise ValueError('invalid escalated or effort')
    status = row.get('status', 'completed')
    if status not in ['completed', 'failed', 'cancelled', 'incomplete', 'interrupted']:
        raise ValueError('invalid status')
    counts = [row[key] for key in ['findings', 'confirmed', 'rejected']]
    plausible = row.get('plausible', 0)
    if status == 'completed' or any(v is not None for v in counts):
        if any(type(v) is not int or v < 0 for v in counts + [plausible]):
            raise ValueError('invalid finding counts')
        if row['confirmed'] + row['rejected'] + plausible > row['findings']:
            raise ValueError('assessment counts exceed findings')
    if new:
        for key in ['taskId', 'runId']:
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('new record requires ' + key)
        if type(row.get('round')) is not int or row['round'] not in [1, 2]:
            raise ValueError('new record requires round 1 or 2')
        if row.get('triageSource') not in ['decision_model', 'manual'] or row.get('coverage') not in ['full', 'partial', 'none']:
            raise ValueError('new record requires triageSource and coverage')
        if 'status' not in row or 'plausible' not in row:
            raise ValueError('new record requires status and plausible')
        if status == 'completed' and row['confirmed'] + row['rejected'] + plausible != row['findings']:
            raise ValueError('all findings must be assessed before logging')
    return row


def append_record(row, path=SCOREBOARD):
    validate_record(row, new=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, 'a+', encoding='utf-8') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        contents = handle.read()
        skipped = []
        duplicate = False
        for index, line in enumerate(contents.splitlines(), 1):
            if not line.strip():
                continue
            existing = None
            try:
                existing = json.loads(line)
                validate_record(existing)
            except (ValueError, TypeError):
                # Keep bad history intact, but do not conceal a conflicting task ID.
                if isinstance(existing, dict) and existing.get('taskId') == row['taskId']:
                    raise ValueError('existing task record is invalid; do not append a replacement')
                skipped.append(index)
                continue
            if existing.get('taskId') == row['taskId']:
                if existing == row:
                    duplicate = True
                else:
                    raise ValueError('taskId already has a different record; do not overwrite it')
        if duplicate:
            return {'appended': False, 'taskId': row['taskId'], 'skippedLines': skipped}
        handle.seek(0, os.SEEK_END)
        if contents and not contents.endswith('\n'):
            handle.write('\n')
        handle.write(json.dumps(row, allow_nan=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
    return {'appended': True, 'taskId': row['taskId'], 'skippedLines': skipped}


def ranking(work_type, path=SCOREBOARD):
    groups, seen, skipped = {}, set(), []
    if not Path(path).exists():
        return {'models': [], 'skippedLines': []}
    for index, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = validate_record(json.loads(line))
        except (ValueError, TypeError):
            skipped.append(index)
            continue
        if row['workType'] != work_type or row.get('status', 'completed') != 'completed':
            continue
        identity = (row.get('runId', row['date'] + ':' + row['slug']), row['provider'], row['model'])
        # Rebuttal rounds are not additional independent reviews.
        if identity in seen:
            continue
        seen.add(identity)
        key = (row['provider'], row['model'])
        group = groups.setdefault(key, {'provider': key[0], 'model': key[1], 'reviews': 0, 'confirmed': 0, 'rejected': 0})
        group['reviews'] += 1
        group['confirmed'] += row['confirmed']
        group['rejected'] += row['rejected']
    for group in groups.values():
        group['eligibleForRanking'] = group['reviews'] >= 5
        group['confirmedPerReview'] = group['confirmed'] / group['reviews']
        group['demote'] = group['eligibleForRanking'] and group['rejected'] > group['confirmed']
    return {'models': list(groups.values()), 'skippedLines': skipped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('prepare')
    create.add_argument('packet')
    create.add_argument('--author', action='append', required=True, help='Provider:model, or unknown when provenance is unavailable')
    create.add_argument('--chair', required=True, help='Provider:model')
    create.add_argument('--timeout-seconds', type=int, default=600)
    append = sub.add_parser('append')
    append.add_argument('record')
    rank = sub.add_parser('rank')
    rank.add_argument('work_type', choices=['code', 'plan', 'copy', 'mixed'])
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.packet, args.author, args.chair, args.timeout_seconds)
    elif args.command == 'append':
        result = append_record(json.loads(Path(args.record).read_text(encoding='utf-8')))
    else:
        result = ranking(args.work_type)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError):
        # Never echo packet contents or a malformed record into the transcript.
        raise SystemExit('Review state failed. Check input fields and file access. Existing records were not replaced.')
