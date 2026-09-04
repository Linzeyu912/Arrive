from datetime import datetime, timezone

from arrive.time_utils import dual_time


def test_dual_time_derives_both_columns_from_one_truncated_instant():
    value = datetime(2026, 9, 4, 11, 30, 0, 500000, tzinfo=timezone.utc)

    iso, epoch = dual_time(value)

    assert iso == "2026-09-04T11:30:00+00:00"
    assert epoch % 1000 == 0
    assert epoch == int(
        datetime(2026, 9, 4, 11, 30, 0, tzinfo=timezone.utc).timestamp() * 1000
    )
