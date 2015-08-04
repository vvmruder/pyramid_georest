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
    <h1 class="navbar-text">${features[0].__class__.__name__}</h1>
</nav>

<div class="container-fluid" style="margin-top: 100px;">

    % for feature in features:

    <div class="panel panel-default center-block" style="width: 80%;">

        <div class="panel-heading">
            <h3 class="panel-title">
                Datensatz
                % for pk in feature.pk_column_names():
                    &nbsp;${feature.as_dict().get(pk)}
                % endfor
            </h3>
        </div>

        <div class="panel-body">

            <dl class="dl-horizontal">
                % for key, value in feature.as_dict().iteritems():
                    <dt>${key}</dt>
                    <dd>${value}</dd>
                % endfor
            </dl>

        </div>

    </div>

    % endfor

</div>