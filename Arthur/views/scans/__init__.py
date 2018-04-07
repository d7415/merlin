# This file is part of Merlin/Arthur.
# Merlin/Arthur is the Copyright (C)2009,2010 of Elliot Rosemarine.

# Individual portions may be copyright by individual contributors, and
# are included in this collective work with permission of the copyright
# owners.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
 
from django.conf.urls import include, url
from Core.paconf import PA
from Arthur.views.scans import list as slist, request, planet, galaxy

urlpatterns = [
  url(r'^scans?/', include( [
    url(r'^$', slist.scans, name="scans"),
    url(r'^(?P<x>\d+)[. :\-](?P<y>\d+)[. :\-](?P<z>\d+)/',
        include(
            [url(r'^$', planet.planet, name="planet_scans"),
            url(r'^(?P<types>['+"".join([type.lower() for type in PA.options("scans")])+']+)/$', planet.types),
            ] + [url(r'^'+type.lower()+'\w*/$', planet.scan, {"type":type}, name="planet_scan_"+type.lower()) for type in PA.options("scans")]
        )),
    url(r'^(?P<x>\d+)[. :\-](?P<y>\d+)/',
        include( [
            url(r'^$', galaxy.galaxy, name="galaxy_scans"),
            url(r'^(?P<types>['+"".join([type.lower() for type in PA.options("scans")])+']+)/$', galaxy.types)
        ])),
    url('^(?P<tick>\d+)/$', slist.tick, name="scan_tick"),
    url('^(?P<tick>\d+)/(?P<id>\w+)/$', planet.id, name="scan_id"),
    url('^group/(?P<id>\w+)/$', slist.group, name="scan_group_id"),
  ])),
  url('^(?:scans?/)?requests?/$', request.requests, name="requests"),
  url(r'^(?:scans?/)?requests?/', include(request)),
]
