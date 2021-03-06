# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from shuup.admin.base import AdminModule, MenuEntry, Notification
from shuup.admin.utils.permissions import get_default_model_permissions
from shuup.admin.utils.urls import (
    admin_url, derive_model_url, get_edit_and_list_urls
)
from shuup.notify.enums import Priority
from shuup.notify.models import Notification as NotificationModel
from shuup.notify.models import Script


class NotifyAdminModule(AdminModule):
    name = _(u"Notifications")
    breadcrumbs_menu_entry = MenuEntry(name, "shuup_admin:notify.script.list")

    def get_urls(self):
        permissions = get_default_model_permissions(NotificationModel)
        return [
            admin_url(
                "notify/script-item-editor/",
                "shuup.notify.admin_module.views.script_item_editor",
                name="notify.script-item-editor",
                permissions=permissions
            ),
            admin_url(
                "notify/script/content/(?P<pk>\d+)/",
                "shuup.notify.admin_module.views.EditScriptContentView",
                name="notify.script.edit-content",
                permissions=permissions
            ),
            admin_url(
                "notify/mark-read/(?P<pk>\d+)/$",
                self.mark_notification_read_view,
                name="notify.mark-read",
                permissions=permissions
            ),
        ] + get_edit_and_list_urls(
            url_prefix="^notify/script",
            view_template="shuup.notify.admin_module.views.Script%sView",
            name_template="notify.script.%s",
            permissions=permissions
        )

    def get_menu_category_icons(self):
        return {self.name: "fa fa-envelope-o"}

    def get_menu_entries(self, request):
        category = _("Notifications")
        return [
            MenuEntry(
                text=_("Notification scripts"), icon="fa fa-code",
                url="shuup_admin:notify.script.list",
                category=category, aliases=[_("Show notification scripts")]
            )
        ]

    def get_required_permissions(self):
        return get_default_model_permissions(NotificationModel)

    @csrf_exempt
    def mark_notification_read_view(self, request, pk):
        if request.method == "POST":
            try:
                notif = NotificationModel.objects.for_user(request.user).get(pk=pk)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "no such notification"})
            notif.mark_read(request.user)
            return JsonResponse({"ok": True})
        return JsonResponse({"error": "POST only"})

    def get_notifications(self, request):
        notif_qs = NotificationModel.objects.unread_for_user(request.user).order_by("-id")[:15]

        for notif in notif_qs:
            if notif.priority == Priority.HIGH:
                kind = "warning"
            elif notif.priority == Priority.CRITICAL:
                kind = "danger"
            else:
                kind = "info"

            yield Notification(
                text=notif.message,
                url=notif.url,
                kind=kind,
                dismissal_url=reverse("shuup_admin:notify.mark-read", kwargs={"pk": notif.pk}),
                datetime=notif.created_on
            )

    def get_model_url(self, object, kind):
        return derive_model_url(Script, "shuup_admin:notify.script", object, kind)
