#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import datetime
from .suffix_handle import modify
from .exceptions import AbnormalLMTFormat, AbnoramlLMTString, UnformatLMTString
from . import LMT_FORMAT_NORMAL, LMT_FORMAT_ABNORMAL


def parse_time(lmt_string: str):
    # if len(lmt_string) > 100:
    if len(str(lmt_string)) > 100:
        raise AbnoramlLMTString("lmt too long! please check!" + lmt_string[:100])

    if lmt_string.isdigit():
        lmt_int = int(lmt_string)
        if len(str(lmt_int)) > 10:
            lmt_int = lmt_int // 1000
        return lmt_int

    lmt_string = modify(lmt_string)

    for format in LMT_FORMAT_NORMAL:
        lmt_object = try_transfer_datetime(lmt_string, format)
        if lmt_object is not None:
            return try_get_timestamp(lmt_object)

    for format in LMT_FORMAT_ABNORMAL:
        lmt_object = try_transfer_datetime(lmt_string, format)
        if lmt_object is not None:
            raise AbnormalLMTFormat("wrong lmt format：" + lmt_string)

    raise UnformatLMTString("no matched lmt：" + lmt_string)


def try_get_timestamp(lmt_datetime):
    try:
        timestamp = lmt_datetime.timestamp()
        return int(timestamp)
    except OSError:
        return (lmt_datetime - datetime.datetime(1970, 1, 1)).total_seconds()
    except Exception as e:
        print("catch error", e)


def try_transfer_datetime(lm_string, format):
    try:
        result = datetime.datetime.strptime(lm_string, format)
    except ValueError:
        return None
    return result

def parse_time_stamp(lmt_timestamp):
    try:
        return  datetime.datetime.fromtimestamp(lmt_timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except OSError:
        return  datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds= lmt_timestamp)
    except Exception:
        print("Error in converting timestamp to string, data:", lmt_timestamp)
