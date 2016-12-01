/**
 *  Copyright (c) 2012 - 2016, GIS-Fachstelle des Amtes für Geoinformation des Kantons Basel-Landschaft
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
 * Created by Clemens Rudert on 30.11.16.
 */

<%
    from pyramid_georest.routes import route_prefix
    from pyramid_georest.lib import camel_casify
    import simplejson
    api_name = request.registry.pyramid_georest_requested_api.name
    schema_name = request.matchdict['schema_name']
    table_name = request.matchdict['table_name']
    application_base_url = request.application_url
    if route_prefix is not None and len(route_prefix) > 0:
        application_base_url += '/' + route_prefix
    module_name = 'rest{0}'.format(camel_casify('{api_name} {schema_name} {table_name}'.format(
        api_name=api_name,
        schema_name=schema_name,
        table_name=table_name
    )))
%>

var app = angular.module('${module_name}', []);

app.Model = function () {
    function Model() {
        var description = angular.fromJson(${simplejson.dumps(model_description.as_dict())|n});
        angular.forEach(description, function (value, name) {
            this[name] = value;
        });
        this.getIntegerColumns = function(){
            var integerColumns = [];
            angular.forEach(description.columns, function (column_metadata, column_name) {
                if(column_metadata.type == 'INTEGER'){
                    integerColumns.push(column_name);
                }
            });
            return integerColumns;
        };
        this.getRelationShips = function(){
            return description.relationships;
        };
        this.getPrimaryKeyColumnNames = function(){
            return description.primary_key_column_names;
        };
        this.getColumnDescriptions = function(){
            return description.columns;
        };
        this.getGeometryColumNames = function(){
            return description.geometry_column_names;
        }
    }
    return Model;
};

app.module.factory('${module_name}Model', app.Model);

app.restResource = function ($http, ${module_name}Model) {
    var restfulFeature = function (properties){
        this.manipulated = false;
        this.persisted = false;
        this.errors = {};
        this.urlCreate = '${application_base_url}/${api_name}/${schema_name}/${table_name}/create/geojson';
        this.urlUpdate = '${application_base_url}/${api_name}/${schema_name}/${table_name}/update/geojson/';
        this.model = new ${module_name}Model;
        var formatter = new ol.format.GeoJSON();

        if(!angular.isDefined(properties)){
            properties = {};
            angular.forEach(this.model.getColumnDescriptions(), function (description, name) {
                properties[name] = description.default;
            });
        }

        this.create = function(){
            var self = this;
            $http({
                method: 'POST',
                url: self.urlCreate,
                data: {
                    feature: formatter.writeFeatureObject(self)
                }
            }).then(function successCallback(response) {
                self.manipulated = false;
                self.persisted = true;
                if(self.successCallback != null) {
                    self.successCallback(self, response);
                    self.successCallback = null;
                }
            }, function errorCallback(response) {
                if(self.errorCallback != null) {
                    self.errorCallback(self, response);
                    self.successCallback = null;
                }
            });
        };
        this.update = function(){
            var self = this;
            var primary_key_values = [];
            angular.forEach(self.model.getPrimaryKeyColumnNames(), function(name){
                primary_key_values.push(self.get(name));
            });
            $http({
                method: 'POST',
                url: self.urlUpdate + primary_key_values.join('/'),
                data: {
                    feature: formatter.writeFeatureObject(self)
                }
            }).then(function successCallback(response) {
                self.manipulated = false;
                self.persisted = true;
                if(self.successCallback != null) {
                    self.successCallback(self, response);
                    self.successCallback = null;
                }
            }, function errorCallback(response) {
                if(self.errorCallback != null) {
                    self.errorCallback(self, response);
                    self.successCallback = null;
                }
            });
        };
        ol.Feature.call(this, properties);
    };
    ol.inherits(restfulFeature, ol.Feature);
    return restfulFeature;
};

app.restResource['$inject'] = ['$http', '${module_name}Model'];
app.module.factory('${module_name}Resource', app.restResource);

app.restCollection = function ($http, ${module_name}Resource) {
    var restfulCollection = function (settings){
        this.urlRead = '${application_base_url}/${api_name}/${schema_name}/${table_name}/read/geojson';

        this.new = function(){
            var rr = new ${module_name}Resource();
            this.push(rr);
            return rr;
        };

        this.getByFilter = function(filter, success, error){
            var self = this;
            var formatter = new ol.format.GeoJSON();
            $http({
                method: 'POST',
                url: self.urlRead,
                data: {filter: filter}
            }).then(function successCallback(response) {
                self.clear();
                angular.forEach(response.data.features, function (item) {
                    var feature = formatter.readFeature(item);
                    var resource = new ${module_name}Resource();
                    resource.setProperties(feature.getProperties());
                    resource.setGeometry(feature.getGeometry());
                    resource.persisted = true;
                    self.push(resource);
                });
                if (angular.isDefined(success)){
                    success(self, response);
                }
            }, function errorCallback(response) {
                if (angular.isDefined(error)){
                    error(self, response);
                }
            });
        };
        this.select = function (index) {
            this.selected = this.item(index);
        };
        ol.Collection.call(this, []);
    };
    ol.inherits(restfulCollection, ol.Collection);
    return restfulCollection;
};

app.restCollection['$inject'] = ['$http', '${module_name}Resource'];
app.module.factory('${module_name}Collection', app.restCollection);