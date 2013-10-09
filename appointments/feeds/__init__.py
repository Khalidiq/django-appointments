import datetime
import itertools

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.syndication.views import FeedDoesNotExist

from appointments.conf import settings
from appointments.feeds.atom import Feed
from appointments.feeds.icalendar import ICalendarFeed
from appointments.models import Calendar


class UpcomingEventsFeed(Feed):
    feed_id = "upcoming"

    def feed_title(self, obj):
        return "Upcoming Events for %s" % obj.name

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Calendar.objects.get(pk=bits[0])

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def items(self, obj):
        return itertools.islice(obj.occurrences_after(datetime.datetime.now()),
                                getattr(settings, "FEED_LIST_LENGTH", 10))

    def item_id(self, item):
        return str(item.id)

    def item_title(self, item):
        return item.event.title

    def item_authors(self, item):
        if item.event.creator is None:
            return [{'name': ''}]
        return [{"name": item.event.creator.username}]

    def item_updated(self, item):
        return item.event.created_on

    def item_content(self, item):
        return "%s \n %s" % (item.event.title, item.event.description)


class CalendarICalendar(ICalendarFeed):

    def items(self):
        cal_id = self.args[1]
        cal = Calendar.objects.get(pk=cal_id)

        return cal.events.all()

    def item_uid(self, item):
        return str(item.id)

    def item_start(self, item):
        return item.start

    def item_end(self, item):
        return item.end

    def item_summary(self, item):
        return item.title

    def item_created(self, item):
        return item.created_on