import json
from datetime import datetime, timedelta

local_tz = datetime.now().astimezone().tzinfo


def load_issue(f):
    with open(f, 'r') as fp:
        out = json.load(fp)
        out["properties"]["filename"] = f
        return out


def write_issue(fn, issue):
    with open(fn, 'w') as fp:
        json.dump(issue, fp, indent=4, sort_keys=True)


with open('.index', 'r') as fp:
    index = json.load(fp)


def parse_duration(td):
    t = datetime.strptime(td, "%H:%M")
    return timedelta(hours=t.hour, minutes=t.minute, seconds=0)


def parse_time(t):
    return datetime.strptime(t, "%H:%M")


def parse_date(d, infer_year=False):
    if infer_year:
        d = datetime.strptime(d, "%m-%d").date()
        n = datetime.now()
        return datetime(n.year, d.month, d.day).date()
    return datetime.strptime(d, "%Y-%m-%d").date()


def parse_date_as_datetime(d, infer_year=False):
    if infer_year:
        d = datetime.strptime(d, "%m-%d").date()
        n = datetime.now()
        return datetime(n.year, d.month, d.day).replace(tzinfo=local_tz)
    return datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=local_tz)


def parse_logbook_time_into_date(d):
    return datetime.strptime(d, "%Y-%m-%d %H:%M:%S %z").date()


def parse_logbook_time_into_time(d):
    if d:
        return datetime.strptime(d, "%Y-%m-%d %H:%M:%S %z")
    return None


def date_to_logbook_time(d):
    return d.strftime("%Y-%m-%d %H:%M:%S %z")


def get_time(d):
    if d:
        return parse_logbook_time_into_time(d).time().strftime("%H:%M:%S")
    return "None"


def get_day_of_week(d):
    return d.strftime('%Y-%m-%d - %A')


def index_of_needle(key_getter, l, needle):
    idx=[key_getter(x) for x in l].index(needle)
    return idx, l[idx]


def get_id_of_issue(issue_name):
    project, sub_project, name=issue_name.split("/")
    project_idx, project_obj=index_of_needle(lambda x: x[0], index, project)
    sub_project_idx, sub_project_obj=index_of_needle(lambda x: x[0], project_obj[1], sub_project)
    name_idx, name_obj=index_of_needle(lambda x: x, sub_project_obj[1], name)
    return "/".join([str(project_idx), str(sub_project_idx), str(name_idx)])
