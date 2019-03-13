#-*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import time
from datetime import datetime

from django.core.paginator import InvalidPage
from django.utils import timezone
from django.conf import settings

__all__ = [
    'page_key',
    'to_page_key',
    'InvalidPage']

PAGE_RE = re.compile(r'^(?P<value>[0-9]+\.[0-9]{6})-(?P<pk>[0-9]+)$')


def _make_aware_maybe(dt):
    if not getattr(settings, 'USE_TZ', False):
        return dt
    if timezone.is_aware(dt):
        return dt.astimezone(timezone.utc)
    return timezone.make_aware(dt, timezone=timezone.utc)


def _fromtimestamp(ts):
    if not getattr(settings, 'USE_TZ', False):
        return datetime.fromtimestamp(ts)
    return datetime.utcfromtimestamp(ts)


def page_key(raw_page):
    """
    Parse a raw page value of ``timestamp-pk`` format.
    Return a tuple of (timestamp, pk)

    :raises: ``InvalidPage``
    """
    if not raw_page:
        return None, None
    m = re.match(PAGE_RE, raw_page)
    if m is None:
        raise InvalidPage('Bad key format')
    try:
        timestamp = _fromtimestamp(float(m.group('value')))
    except (OverflowError, ValueError):
        raise InvalidPage('Key out of range')
    return _make_aware_maybe(timestamp), m.group('pk')


def to_page_key(value=None, pk=None):
    """Serialize a value and pk to `timestamp-pk`` format"""
    if value is None:
        return ''
    value = _make_aware_maybe(value)
    try:
        timestamp = value.timestamp()
    except AttributeError:
        timestamp = time.mktime(value.timetuple()) + value.microsecond / 1e6
    return '{:.6f}-{}'.format(timestamp, pk)
