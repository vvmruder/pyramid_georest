/**
 * Copyright (c) 2012 - 2015, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
 * All rights reserved.
 *
 * This program is free software and completes the GeoMapFish License for the geoview.bl.ch specific
 * parts of the code. You can redistribute it and/or modify it under the terms of the GNU General
 * Public License as published by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
 * even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * The above copyright notice and this permission notice shall be included in all copies or substantial
 * portions of the Software.
 *
 * Created by u207027 on 04.08.15.
 */

var blRestDoc = angular.module('blRestRead', [])
    .controller('BLRestReadCtrl', ['$scope', '$location', function($scope, $location) {

        // Open url is same window
        $scope.goTo = function(target) {
            var current = $location.absUrl();
            window.location = current + '/' + target;
        };

    }]);