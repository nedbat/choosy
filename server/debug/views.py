"""Views for diagnostic views used by developers."""

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import HttpResponse

import logging
import os
import sys

log = logging.getLogger(__name__)

@staff_member_required
def dump_settings(request):
    """Dump all the settings to the log file.

    Don't write them to the response: insecure.

    """
    log.info("----- Django settings:")
    for a in dir(settings):
        if a.startswith('__'):
            continue
        log.info("%s: %r" % (a, getattr(settings, a)))
    return HttpResponse("Settings have been logged.")

@staff_member_required
def raise_error(request):
    """Generate an exception.  How else will we know if our stack traces are working?"""
    msg = request.GET.get("msg", "Something bad happened! (on purpose)")
    raise Exception(msg)

@staff_member_required
def send_email(request):
    """Send an email to test the mail-sending infrastructure."""
    msg = request.GET.get("msg", "Test of sending email")
    send_mail(msg, 'The body also says "%s"' % msg, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
    return HttpResponse("An email was sent to %s" % request.user.email)

@staff_member_required
def dump_environment(request):
    """Dump all the environment variables to the log file."""
    log.info("----- Environment variables:")
    for name, value in sorted(os.environ.items()):
        log.info("%s: %r" % (name, value))
    return HttpResponse("Environment variables have been logged.")

@staff_member_required
def dump_modules(request):
    """Dump all the modules and their version to the log file."""
    log.info("----- Python modules:")
    for name, module in sorted(sys.modules.items()):
        if not module:
            continue
        file = getattr(module, '__file__', '<builtin>')
        for vattr in ['__version__', '__VERSION__', 'version', 'VERSION']:
            if hasattr(module, vattr):
                version = ", version %r" % (getattr(module, vattr),)
                break
        else:
            version = ''
        log.info("%s: %s%s" % (name, file, version))
    return HttpResponse("Python modules have been logged.")
