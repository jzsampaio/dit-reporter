import glob
import json
from os import path
import argparse
import os
import datetime
import pytz
from tabulate import tabulate

class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

SHORT_LEN = 4

parser = argparse.ArgumentParser()
parser.add_argument('entry',
                    action=readable_dir,
                    help='Entry point. Specify as path')
parser.add_argument('start',
                    help='Start date, input format should be yyyy-mm-dd')
parser.add_argument('end',
                    help='End date, input format should be yyyy-mm-dd')
parser.add_argument('-s',
                    '--short',
                    action='store_true',
                    help='Display shortened task ID')
parser.add_argument('-g',
                    '--group',
                    type=str,
                    help='Shows only tasks pertaining to the selected group.')
parser.add_argument('-sg',
                    '--subgroup',
                    type=str,
                    help='Shows only tasks pertaining to the selected sub-group.')
parser.add_argument('-t',
                    '--task',
                    type=str,
                    help='Shows only tasks pertaining to the selected task.')

def load(f):
    with open(f, 'r') as fp:
        out = json.load(fp)
        out["properties"]["filename"] = f
        return out

def parse_date(d):
    return datetime.datetime.strptime(d, "%Y-%m-%d").date()

def parse_logbook_time(d):
    return datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S %z").date()

def parse_logbook_time2(d):
    if d:
        return datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S %z")
    return None

def get_time(d):
    if d:
        return parse_logbook_time2(d).time().strftime("%H:%M:%S")
    return "None"

def get_day_of_week(d):
    return d.strftime('%Y-%m-%d - %A')

def crop_str(s, l, c):
    return s[:SHORT_LEN] if c and l > SHORT_LEN else s

def crop_issue_name(s, c):
    return '/'.join([crop_str(e, len(e), c) for e in s.split('/')])

def daily_report(d, start, end, short, group=None, subgroup=None, task=None):
    try:
        tasks = [load(f) for f in glob.glob(f"""{d}/{group or '*'}/{subgroup or '*'}/{task or '*'}""")]
    except:
        Exception('Invalid group passed')

    dates_in_range = [(start + datetime.timedelta(days=x)) for x in range(0, (end - start).days)]
    daily_logbook = {d: [] for d in dates_in_range}

    for t in tasks:
        logbook = [e for e in t["logbook"] if parse_logbook_time(e["in"]) >= start and parse_logbook_time(e["in"]) < end]
        for e in logbook:
            date = parse_logbook_time(e["in"])
            for k in ["title", "properties", "created_at", "updated_at", "concluded_at", "notes", "filename"]:
                e[k] = t.get(k, None)
            daily_logbook[date].append(e)

    sorted_logbook = {x[0]: sorted(x[1], key=lambda z: parse_logbook_time2(z['in'])) for x in daily_logbook.items()}

    for d in sorted(sorted_logbook.keys()):
        total = datetime.timedelta(0)
        rows = []
        for e in sorted_logbook[d]:
            s = parse_logbook_time2(e['in'])
            x = parse_logbook_time2(e['out'])
            if not x:
                x = datetime.datetime.now(pytz.timezone(s.tzinfo))
            total += x - s

            issue_name = e['properties']['filename'].replace("./", "")

            rows.append([get_time(e['in']),
                         get_time(e['out']),
                         crop_issue_name(issue_name, short),
                         e['title']])
        print('-' * 24)
        print(f"""[Date] {get_day_of_week(d)} [Total] {total}""")
        print('-' * 24)
        print(tabulate(rows, headers=["start", "end", "task id", "title"]))



kwargs = parser.parse_args()
entry_point = kwargs.entry
start = parse_date(kwargs.start)
end = parse_date(kwargs.end)
short = kwargs.short
group = None
subgroup = None
task = None
if kwargs.group:
    group = kwargs.group
    if not os.path.isdir(entry_point + '/' + group):
        raise Exception('Group should be a valid folder under [entry]')
if kwargs.subgroup:
    subgroup = kwargs.subgroup
    if group and not os.path.isdir(entry_point + '/' + group + '/' + subgroup):
        raise Exception('Subgroup should be a valid folder under [entry/group] if group is specified.')
    elif not any(map(lambda x: x.endswith(subgroup), [e[0] for e in os.walk(entry_point)])):
        raise Exception('Subgroup should be a valid folder under [entry/*]')
if kwargs.task:
    task = kwargs.task
    if not any(map(lambda x: task in x, [e[2] for e in os.walk(entry_point)])):
        raise Exception('Task should be a valid file under [entry/*/*]')
daily_report(entry_point, start, end, short, group=group, subgroup=subgroup, task=task)
