<!DOCTYPE html>

<!--
Copyright (c) 2012 - 2015, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
All rights reserved.

This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
parts of the code. You can redistribute it and/or modify it under the terms of the GNU General 
Public License as published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

Created by vvmruder on 29.07.15.
-->
<%inherit file="pyramid_rest:templates/layout.mako"/>

<nav class="navbar navbar-inverse navbar-fixed-top">
    <h1 class="navbar-text">Dokumentation zur Rest-Schnittstelle</h1>
</nav>

<div class="container-fluid" style="margin-top: 100px;">
    <div class="panel panel-default center-block" style="width: 80%;">

        <div class="panel-body" ng-app>
            <p>
                <div class="list-group">
                    <a href=${path} target="_blank" class="list-group-item">
                        <h4 class="list-group-item-heading">
                            <span>${name} </span>
                            <span class="glyphicon glyphicon-circle-arrow-right pull-right"></span>
                        </h4>
                        <p class="list-group-item-text">
                            ${short_description}
                        </p>
                    </a>
                </div>
            </p>
            <div class="alert alert-warning">
                Bitte bedenken Sie, dass für alle Datensätze Berechtigungen eingeholt werden müssen. Es werden über
                diese Schnittstelle keine Daten öffentlich und frei zugänglich angeboten. Sollten Sie Interesse an
                dem Zugriff haben wenden Sie sich bitte an den
                <a href="mailto:${request.registry.pyramid_rest_support_mail}">
                    ${request.registry.pyramid_rest_support_name}
                </a>.
            </div>

        </div>
    </div>
</div>