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
                Über diese Schnittstelle erhalten Sie Zugriff auf Daten verschiedenster Datenbanken. Die Funktionen dieser
                Schnittstelle sind im Folgenden kurz dargelegt.
            </p>
            <p>
                Das zugrunde liegende Prinzip dieser Schnittstelle ist die REST-Methode
                (siehe  <a href="https://de.wikipedia.org/wiki/Representational_State_Transfer">Wikipedia</a>). Im Grossen und
                Ganzen lässt sich diese Methode auf folgenden Grundsatz reduzieren:
            </p>

            <div class="well well-sm lead text-center">Jede Tabelle hat eine eigene Grund-URL (Ressource)</div>

            <p>
                Jede dieser Ressourcen ist wiederum unterteilt um Zugriff auf die verschiedenen Methoden zu ermöglichen. Diese
                Methoden sind in aller erster Linie:
                <ol>
                    <li>alle Elemente der Tabelle lesen (read)</li>
                    <li>exakt ein Element der Tabelle lesen (read_one)</li>
                    <li>exakt ein Element in die Tabelle einfügen (create)</li>
                    <li>exakt ein Element in der Tabelle verändern (update)</li>
                    <li>exakt ein Element in der Tabelle löschen (delete)</li>
                </ol>
            </p>

            <p>
                Zusätzlich zu diesen Möglichkeiten (die zu den Standards gehören) bietet diese REST-Schnittstelle
                einiges mehr:
                <ol>
                    <li>alle Elemente der Tabelle lesen (read) + Filterung über Attributwerte der Tabelle</li>
                    <li>alle Elemente der Tabelle zählen (count) + Filterung über Attributwerte der Tabelle</li>
                    <li>Metainformationen der Tabelle (model)</li>
                </ol>
            </p>

            <p>
                Zu jedem Service gibt es eine seperate Dokumentation. Wollen Sie erfahren, wie ein konkreter Service zu
                nutzen ist? Dann können Sie die jeweilige Dokumentation aufrufen, indem Sie auf den Eintrag in der
                folgenden Auflistung klicken.
            <p>
            <div class="alert alert-warning">
                Bitte beachten Sie, dass für manche Datensätze Berechtigungen eingeholt werden müssen. Es werden über
                diese Schnittstelle nur manche Daten öffentlich und frei zugänglich angeboten. Sollten Sie Interesse an
                dem Zugriff haben wenden Sie sich bitte an den
                <a href="mailto:${request.registry.pyramid_rest_support_mail}">
                    ${request.registry.pyramid_rest_support_name}
                </a>
                Berechtigungen sind in der Auflistung ersichtlich.
            </div>
            <p>
                Zur Zeit stehen über diese Schnittstelle folgende Datensätze zur Verfügung:
            </p>
            <p>
                <div class="list-group">
                    % for service in request.registry.pyramid_rest_services:
                        <a href=${request.route_url('/' + service.config.get('path'))} class="list-group-item">
                            <h4 class="list-group-item-heading">
                                <span>${service.config.get('name')} </span>
                                <span class="glyphicon glyphicon-circle-arrow-right pull-right"></span>
                            </h4>
                            <p class="list-group-item-text">
                                ${service.config.get('description')}
                            </p>
                        </a>
                    % endfor
                </div>
            </p>
        </div>
    </div>
</div>