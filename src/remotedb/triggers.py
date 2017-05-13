import functools
import itertools
import logging

from firebase.firebase import FirebaseApplication

from django.conf import settings

from django_q import tasks

from events.models import (
    CustomEvent, KeynoteEvent, ProposedTalkEvent, SponsoredEvent,
)
from proposals.models import TalkProposal

from . import dumpers


logger = logging.getLogger(__name__)


def mock_on_debug(f):
    """Mock out decorated function when `settings.DEBUG` is True.
    """
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if settings.DJANGO_Q_DEBUG:
            logger.info('Called {0} with args={args!r}, kwargs={kw!r}'.format(
                f.__name__, args=args, kw=kwargs,
            ))
            return
        return f(*args, **kwargs)

    return wrapped


def update_firebase(key, data):
    app = FirebaseApplication(settings.FIREBASE_URL)
    app.put(settings.FIREBASE_DB, key, data)


def _sync_proposal_detail(proposal):
    data = {str(proposal.pk): dumpers.dump_proposal(proposal)}
    update_firebase('events', data)


@mock_on_debug
def sync_proposal_detail(proposal):
    tasks.async(_sync_proposal_detail, proposal)


def _sync_sponsored_talk_detail(event):
    detail_data = dumpers.dump_sponsored_event_detail(event)
    data = {'sponsored_{}'.format(event.pk): detail_data}
    update_firebase('events', data)


@mock_on_debug
def sync_sponsored_talk_detail(event):
    tasks.async(_sync_sponsored_talk_detail, event)


def _sync_schedule():
    custeom_event_qs = (
        CustomEvent.objects
        .select_related('begin_time', 'end_time')
    )
    keynote_event_qs = (
        KeynoteEvent.objects
        .select_related('begin_time', 'end_time')
    )
    proposed_talk_event_qs = (
        ProposedTalkEvent.objects
        .select_related('begin_time', 'end_time', 'proposal__submitter')
    )
    sponsored_event_qs = (
        SponsoredEvent.objects
        .select_related('begin_time', 'end_time', 'host')
    )
    schedule_data = dumpers.dump_schedule(itertools.chain(
        custeom_event_qs,
        keynote_event_qs,
        proposed_talk_event_qs,
        sponsored_event_qs,
    ))
    data = {
        key: {'date': key, 'slots': value}
        for key, value in schedule_data.items()
    }
    update_firebase('schedule', data)


@mock_on_debug
def sync_schedule():
    tasks.async(_sync_schedule)


def _sync_user_events(user):
    data = {
        'sponsored_{}'.format(e.pk): dumpers.dump_sponsored_event_detail(e)
        for e in SponsoredEvent.objects.filter(host=user)
    }
    data.update({
        str(p.pk): dumpers.dump_proposal(p)
        for p in TalkProposal.objects.filter_viewable(user=user)
    })
    if data:
        update_firebase('events', data)


@mock_on_debug
def sync_user_events(user):
    tasks.async(_sync_user_events, user)
