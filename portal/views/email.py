# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from datetime import timedelta

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages

from portal.models import EmailVerification, UserProfile
from portal.helpers.email import send_email, NOTIFICATION_EMAIL
from portal.app_settings import CONTACT_FORM_EMAILS


def verify_email(request, token):
    verifications = EmailVerification.objects.filter(token=token)

    if len(verifications) != 1:
        return render(request, 'portal/email_verification_failed.html')

    verification = verifications[0]

    if verification.used or (verification.expiry - timezone.now()) < timedelta():
        return render(request, 'portal/email_verification_failed.html')

    verification.used = True
    verification.save()

    user = verification.user
    user.awaiting_email_verification = False
    user.save()

    if verification.email:
        user.user.email = verification.email
        user.user.save()

    messages.success(request, 'Your email address was successfully verified, please log in.')

    if hasattr(user, 'student'):
        return HttpResponseRedirect(reverse_lazy('play'))
    elif hasattr(user, 'teacher'):
        return HttpResponseRedirect(reverse_lazy('teach'))

    # default to homepage if something goes wrong
    return HttpResponseRedirect(reverse_lazy('home'))


def send_new_users_report(request):
    new_profiles_count = UserProfile.objects.filter(user__date_joined__gte=timezone.now() - timedelta(days=7)).count()
    send_email(NOTIFICATION_EMAIL, CONTACT_FORM_EMAILS, "new users",
               "There are %d new users this week!" % new_profiles_count)
    return HttpResponse('success')
