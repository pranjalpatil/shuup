# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import pytest

from shuup.simple_cms.plugins import PageLinksPlugin
from shuup_tests.front.fixtures import get_jinja_context

from .utils import create_page


@pytest.mark.django_db
@pytest.mark.parametrize("show_all_pages", [True, False])
def test_page_links_plugin_hide_expired(show_all_pages):
    """
    Make sure plugin correctly filters out expired pages based on plugin
    configuration
    """
    context = get_jinja_context()
    page = create_page(eternal=True, visible_in_menu=True)
    another_page = create_page(eternal=True, visible_in_menu=True)
    plugin = PageLinksPlugin({"pages": [page.pk, another_page.pk], "show_all_pages": show_all_pages})
    assert page in plugin.get_context_data(context)["pages"]

    page.available_from = None
    page.available_to = None
    page.save()
    assert page in plugin.get_context_data(context)["pages"]

    plugin.config["hide_expired"] = True
    pages_in_context = plugin.get_context_data(context)["pages"]
    assert page not in pages_in_context
    assert another_page in pages_in_context


@pytest.mark.django_db
def test_page_links_plugin_show_all():
    """
    Test that show_all_pages forces plugin to return all visible pages
    """
    context = get_jinja_context()
    page = create_page(eternal=True, visible_in_menu=True)
    plugin = PageLinksPlugin({"show_all_pages": False})
    assert not plugin.get_context_data(context)["pages"]

    plugin = PageLinksPlugin({"show_all_pages": True})
    assert page in plugin.get_context_data(context)["pages"]
