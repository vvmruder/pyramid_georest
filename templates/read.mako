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

% if len(features) > 0:

    <nav class="navbar navbar-inverse navbar-fixed-top">
        <h1 class="navbar-text">${features[0].__class__.__name__}</h1>
    </nav>

    <div class="container-fluid" style="margin-top: 100px;">

        <div class="panel panel-default center-block" style="width: 80%;">

            <div class="panel-body">

                <table class="table table-striped table-hover">
                    <tr>
                        % for key, value in features[0].as_dict().iteritems():
                            <th>${key}</th>
                        % endfor
                    </tr>
                % for feature in features:
                    <tr>
                        % for key, value in feature.as_dict().iteritems():
                            <td>${value}</td>
                        % endfor
                    </tr>
                % endfor
                </table>

            </div>

        </div>

    </div>

% endif