# -*- coding: utf-8 -*-

from django.dispatch import receiver, Signal
from django.db.models.signals import post_save
from services.models import Service, SlaCache


@receiver(post_save, sender=Service)
def precache_sla(sender, **kwargs):
    """Make sure the SLA cache exists after the service is saved."""
    service = kwargs['instance']
    if len(SlaCache.objects.filter(service_id=service.id)) == 0:
        # new service - let's generate the cache...
        from services.sla import get_slacache
        slacache = get_slacache(service)
        slacache.save()

        # ...and trigger an initial status check
        from services.monitoring import test_service
        test_service(service)
