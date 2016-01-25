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
    <button type="button" class="btn btn-default btn-lg"
            onclick="location.href='${request.route_url('pyramid_rest_doc')}';">
        <span class="glyphicon glyphicon-arrow-left" aria-hidden="true"></span>
    </button>
    <h1 class="navbar-text">Kurzdokumentation zur Ressource ${name}</h1>
</nav>
<div class="container-fluid" style="margin-top: 100px;">
    <div class="panel panel-default center-block" style="width: 80%;">

        <div class="panel-body" ng-app>

            <p>
                Diese Ressource bietet Ihnen direkten Zugriff auf die Datenbank. Diese Dokumentation wird automatisch
                erstellt. Falls Sie probleme beim Zugriff auf eine der unten beschriebenen URL's haben sollten,
                wenden Sie sich bitte an den Support (<a href="mailto:${request.registry.pyramid_rest_support_mail}">
                    ${request.registry.pyramid_rest_support_name}</a>).
            </p>

            <h2>Datenmodell der Ressource abrufen</h2>

            <p>
                Folgende Formate sind abrufbar:
            </p>

            <p>
            <ul>
                <li>JSON - <a target="_blank" href="${request.route_url(urls.get('model_json'))}">
                    ${request.route_url(urls.get('model_json'))}</a>, HTML-Methode: ${read_method}
                </li>
                <li>XML - <a target="_blank" href="${request.route_url(urls.get('model_xml'))}">
                    ${request.route_url(urls.get('model_xml'))}</a>, HTML-Methode: ${read_method}
                </li>
            </ul>
            </p>

            <p>
                Sie erhalten eine Beschreibung (Metadaten) der zugrunde liegenden Ressource in Form von
                maschinenlesbaren Formaten JSON/XML.
            </p>

            <h2>Datensätze der Ressource zählen</h2>

            <p>
            <ul>
                <li>JSON - <a target="_blank" href="${request.route_url(urls.get('count'))}">
                    ${request.route_url(urls.get('count'))}</a>, HTML-Methode: ${read_method}
                </li>
            </ul>
            </p>

            <h2>Datensätze der Ressource lesen</h2>

            <p>Sie haben die Möglichkeit über diese Schnittstelle Daten zu lesen.</p>

            <h3>Einen einzelnen Datensatz lesen</h3>

            <p>
            <ul>
                <li>
                    JSON - ${request.application_url}${urls.get('read_one_json')}, HTML-Methode: ${read_method}
                </li>
                <li>
                    XML - ${request.application_url}${urls.get('read_one_xml')}, HTML-Methode: ${read_method}
                </li>
                <li>
                    HTML - ${request.application_url}${urls.get('read_one_html')}, HTML-Methode: ${read_method}
                </li>
            </ul>
            </p>
            <p>
                Der Zugriff auf diese URL funktioniert mit dem Primärschlüssel. Aus diesem Grund ist statt des
                Primärschlüsselnamens in der Beispiel-URL der tatsächlich gesuchte Primärschlüsselwert einzusetzen.
                Zum Beispiel statt id => 1.
            </p>


            <h3>Alle Datensätze lesen</h3>

            <p>
            <ul>
                <li>JSON - <a target="_blank" href="${request.route_url(urls.get('read_json'))}">
                    ${request.route_url(urls.get('read_json'))}</a>, HTML-Methode: ${read_method}
                </li>
                <li>XML - <a target="_blank" href="${request.route_url(urls.get('read_xml'))}">
                    ${request.route_url(urls.get('read_xml'))}</a>, HTML-Methode: ${read_method}
                </li>
                <li>HTML - <a target="_blank" href="${request.route_url(urls.get('read_html'))}">
                    ${request.route_url(urls.get('read_html'))}</a>, HTML-Methode: ${read_method}
                </li>
            </ul>
            </p>

            <h2>Datensatz neu erzeugen</h2>

            <p>
            <ul>
                <li>
                    JSON - ${request.application_url}${urls.get('create_one')}, HTML-Methode: ${create_method}
                </li>
            </ul>
            </p>
            <p>
                Mit diesem Dienst haben Sie die Möglichkeit einen neuen Datensatz zu erzeugen. Dazu müssen Sie einen
                POST-Request an den Dienst absetzen, der die Daten zum Erzeugen in folgender Form und im
                <u>Request-Body</u> enthält.
            </p>

            <p>
                Das JSON-Objekt "features" enthält jede Spalte einzeln als Eintrag mit Spaltenname und Wert:
            </p>

            <p>
                <code>
                    <p style="text-indent:30px;">features:{</p>

                    <p style="text-indent:50px;">column-1: <span style="font-style: italic;">value-1</span>,</p>

                    <p style="text-indent:50px;">column-2: <span style="font-style: italic;">value-2</span>,</p>

                    <p style="text-indent:50px;">column-3: <span style="font-style: italic;">value-3</span>,</p>

                    <p style="text-indent:50px;">...,</p>

                    <p style="text-indent:50px;">column-n: <span style="font-style: italic;">value-n</span></p>

                    <p style="text-indent:30px;">}</p>

                </code>
            </p>
            <p>
                Dieser Dienst muss unbedingt mit der HTML-Methode <u>${create_method}</u> angefragt werden. Andere
                Anfragen werden
                mit "404 Not found" vom Server beantwortet.
            </p>

            <h2>Vorhandenen Datensatz editieren</h2>

            <p>
            <ul>
                <li>
                    JSON - ${request.application_url}${urls.get('update_one')}, HTML-Methode: ${update_method}
                </li>
            </ul>
            </p>
            <p>
                Mit diesem Dienst haben Sie die Möglichkeit einen neuen Datensatz zu erzeugen. Dazu müssen Sie einen
                POST-Request an den Dienst absetzen, der die Daten zum Erzeugen in folgender Form und im
                <u>Request-Body</u> enthält.
            </p>

            <p>
                Das JSON-Objekt "features" enthält jede Spalte einzeln als Eintrag mit Spaltenname und Wert:
            </p>

            <p>
                <code>
                    <p style="text-indent:30px;">features:{</p>

                    <p style="text-indent:50px;">column-1: <span style="font-style: italic;">value-1</span>,</p>

                    <p style="text-indent:50px;">column-2: <span style="font-style: italic;">value-2</span>,</p>

                    <p style="text-indent:50px;">column-3: <span style="font-style: italic;">value-3</span>,</p>

                    <p style="text-indent:50px;">...,</p>

                    <p style="text-indent:50px;">column-n: <span style="font-style: italic;">value-n</span></p>

                    <p style="text-indent:30px;">}</p>

                </code>
            </p>
            <p>
                Dieser Dienst muss unbedingt mit der HTML-Methode <u>${update_method}</u> angefragt werden. Andere
                Anfragen werden
                mit "404 Not found" vom Server beantwortet.
            </p>

            <h2>Datensatz löschen</h2>

            <p>
            <ul>
                <li>
                    JSON - ${request.application_url}${urls.get('delete_one')}, HTML-Methode: ${delete_method}
                </li>
            </ul>
            </p>
            <p>
                Dieser Dienst ermöglicht es, einen Datensatz in der Datenbank zu löschen.
            </p>

            <p>
                Das JSON-Objekt "features" enthält jede Spalte einzeln als Eintrag mit Spaltenname und Wert:
            </p>

            <div class="alert alert-warning">
                Achtung! Sie löschen einen Datensatz in der Datenbank. Es wird keine Rückfrage gestellt. Es gibt keinen
                doppelten Boden. Wenn Sie den Dienst aufgerufen haben ist der Datensatz weg!
            </div>
            <p>
                Dieser Dienst muss unbedingt mit der HTML-Methode <u>${delete_method}</u> angefragt werden. Andere
                Anfragen werden
                mit "404 Not found" vom Server beantwortet.
            </p>
        </div>
    </div>
</div>