from datetime import datetime, timezone
from pathlib import Path


class CacheRunLogger:
    def __init__(self, repo_root, run_name='nightly_cache'):
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        logs_dir = Path(repo_root) / 'cache_logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.path = logs_dir / f'{run_name}_{timestamp}.log'
        self._fh = self.path.open('a', encoding='utf-8')
        self._start_utc = datetime.now(timezone.utc)

    def log(self, event, **fields):
        timestamp_utc = datetime.now(timezone.utc).isoformat(timespec='seconds')
        self._fh.write(f'[{timestamp_utc}] {event}\n')
        if fields:
            ordered_items = sorted(fields.items(), key=lambda x: x[0])
            for key, value in ordered_items:
                self._fh.write(f'  {key}: {value}\n')
        self._fh.write('\n')
        self._fh.flush()

    def close(self, success=True):
        end_utc = datetime.now(timezone.utc)
        duration_seconds = (end_utc - self._start_utc).total_seconds()
        self.log('run_finished', success=success, duration_seconds=duration_seconds)
        self._fh.close()
