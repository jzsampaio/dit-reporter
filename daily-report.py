import glob
from os import sys
import datetime
import pytz
from tabulate import tabulate
from ditlib import (
    load_issue,
    parse_logbook_time_into_date,
    parse_logbook_time_into_time,
    get_time,
    get_id_of_issue,
    get_day_of_week,
    parse_date,
)


def daily_report(d, start, end):
    tasks = [load_issue(f) for f in glob.glob(f"""{d}/*/*/*""")]

    dates_in_range = [(start + datetime.timedelta(days=x)) for x in range(0, (end - start).days)]
    daily_logbook = {d: [] for d in dates_in_range}

    for t in tasks:
        logbook = [e for e in t["logbook"] if parse_logbook_time_into_date(e["in"]) >= start and parse_logbook_time_into_date(e["in"]) < end]
        for e in logbook:
            date = parse_logbook_time_into_date(e["in"])
            for k in ["title", "properties", "created_at", "updated_at", "concluded_at", "notes", "filename"]:
                e[k] = t.get(k, None)
            daily_logbook[date].append(e)

    sorted_logbook = {x[0]: sorted(x[1], key=lambda z: parse_logbook_time_into_time(z['in'])) for x in daily_logbook.items()}

    for d in sorted(sorted_logbook.keys()):
        total = datetime.timedelta(0)
        rows = []
        for e in sorted_logbook[d]:
            s = parse_logbook_time_into_time(e['in'])
            x = parse_logbook_time_into_time(e['out'])
            if not x:
                x = datetime.datetime.now(pytz.timezone(s.tzinfo))
            total += x - s

            issue_name = e['properties']['filename'].replace("./", "")

            rows.append([
                get_time(e['in']),
                get_time(e['out']),
                issue_name,
                get_id_of_issue(issue_name),
                e["title"]],
            )
        print('-' * 24)
        print(f"""[Date] {get_day_of_week(d)} [Total] {total}""")
        print('-' * 24)
        print(
            tabulate(
                rows,
                headers=[
                    "start",
                    "end",
                    "task name",
                    "task id",
                    "title",
                ]
            )
        )


def usage():
    print("usage:")
    print("python3 daily-report.py [path] [start-date] [end-date]")
    exit()


argv = sys.argv
argv.pop(0)

if len(argv) < 3:
    usage()
entry_point = argv.pop(0)
start = parse_date(argv.pop(0), True)
end = parse_date(argv.pop(0), True)
daily_report(entry_point, start, end)
