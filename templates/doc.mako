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
            <h4>Jede Tabelle hat eine eigene Grund-URL (Ressource)</h4>

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
                Zusätzlich zu diesen Möglichkeiten (die zu den Standards gehören) bietet diese REST-Schnittstelle einiges mehr:
                <ol>
                    <li>alle Elemente der Tabelle lesen (read) + Filterung über Attributwerte der Tabelle</li>
                    <li>alle Elemente der Tabelle zählen (count) + Filterung über Attributwerte der Tabelle</li>
                    <li>Metainformationen der Tabelle (model)</li>
                </ol>
            </p>

            <p>
                Zum jetzigen Zeitpunkt können über diese Schnittstelle folgende Datensätze angesprochen werden:
            </p>
            <p>
                <select class="form-control" ng-model="service">
                    % for service in request.registry.pyramid_rest_services:
                        <option value=${service}>${service}</option>
                    % endfor
                </select>
            </p>
            <p>
                Bitte bedenken Sie, dass für alle Datensätze Berechtigungen eingeholt werden müssen. Es werden über diese
                Schnittstelle keine Daten öffentlich und frei zugänglich angeboten. Sollten Sie Interesse an dem Zugriff haben
                wenden Sie sich bitte an den <a href="mailto:${request.registry.pyramid_rest_support_mail}">
                ${request.registry.pyramid_rest_support_name}</a>.
            </p>

        </div>
    </div>
</div>