'use strict';

/* Controllers */

angular.module('BambooUI.controllers', [])
    .controller('DatasetListController', ['$scope', function ($scope, BambooAPI) {

    }])
    .controller('InfoCtrl', ['$scope', 'BambooAPI', function ($scope, BambooAPI) {
        $scope.info = {};

        var promise = BambooAPI.queryInfo(dataset_id);
        promise.then(function(result){
            $scope.info = result;
        });

        $scope.check_all = false;
        $scope.has_field_selection = false;

        $scope.setHasFieldSelection = function(value) {
            $scope.has_field_selection = value;
        };

        $scope.toggleHasSelection = function(selector) {
            //$scope.has_field_selection = $(selector).find('input:checked').length > 0;
        };

        $scope.createDasboard = function() {
            var form = $('form#field-list');
            form.attr('action', create_dahsboard_url);
            $('form#field-list').submit();
        };
    }])
    .controller('CalculationsCtrl', ['$scope', 'BambooAPI', '$dialog', function ($scope, BambooAPI, $dialog) {
        $scope.calculations = [];
        $scope.new_calculation = {name: null, formula: null};

        $scope.refreshCalculations = function(){
            var promise = BambooAPI.queryCalculations(dataset_id);
            promise.then(function(result){
                $scope.calculations = result;
            });
        };

        $scope.createCalculation = function () {
            var promise = BambooAPI.addCalculation(
                dataset_id, $scope.new_calculation['name'],
                $scope.new_calculation['formula']);
            promise.then(function(result){
                 $scope.refreshCalculations();
            });
        };

        $scope.removeCalculation = function(calculation){
            var btns = [{result:'cancel', label: 'Cancel'}, {result:'ok', label: 'OK', cssClass: 'btn-primary'}];
            $dialog.messageBox("Delete!", "Delete Calculation?", btns)
                .open()
                .then(function (result) {
                    if(result === 'ok')
                    {
                        BambooAPI.removeCalculation(
                            dataset_id, calculation.name);
                        $scope.calculations.splice(
                            $scope.calculations.indexOf(calculation), 1);
                    }
                });
        };

        $scope.refreshCalculations();
    }])
    .controller('AggregationsCtrl', [function () {

    }])
    .controller('DashboardListCtrl', [function(){

    }])
    .controller('DashboardCtrl', ['$scope', '$http', 'BambooAPI', function(
        $scope, $http, BambooAPI) {
        // request a list of charts from the server
        // TODO: pick a color from the d3 palette
        var colors = ['#1f77b4', '#d62728'];
        $http({method: 'GET', url: charts_url})
            .success(function (data, status, headers, config) {
                $scope.charts = data.charts;
                // for each chart, get its bamboo data
                $scope.charts.forEach(function(chart){
                    bamboo.settings.URL = chart.bamboo_host;

                    var select = {};
                    select[chart['x_field_id']] = 1;
                    if(chart['y_field_id'])
                        select[chart['y_field_id']] = 1;
                    var promise = BambooAPI.querySummary(
                        chart.dataset_id, select);
                    promise.then(function(data){
                        var x_axis_keys = Object.keys(data[chart.x_field_id].summary);
                        var y_axis_keys = [];
                        if(chart['y_field_id'])
                            y_axis_keys = Object.keys(data[chart.y_field_id].summary);

                        // determine our format function
                        if(chart['x_field_id'] && chart['y_field_id'])
                        {
                            formatGroupedData(chart, x_axis_keys, y_axis_keys);
                        }
                        else
                        {
                            formatSummaryData(
                                chart, x_axis_keys,data[chart.x_field_id].summary);
                        }

                        //chart.data =
                        // TODO: create functions for the different chart types that convert bamboo data into target chart's format
                    });
                });
            })
            .error(function (data, status, headers, config) {

            });

        var formatSummaryData = function(chart, x_axis_keys, summary) {
            var item = {key: chart.title, values: []};
            x_axis_keys.forEach(function (x_key, index) {
                var value =
                {
                    label: x_key,
                    value: summary[x_key]
                }
                item.values.push(value);
            });
            chart.data = [item];
        };

        // get grouped summarized data
        var formatGroupedData = function(chart, x_axis_keys, y_axis_keys) {
            var items = [];
            var select = {};
            select[chart.x_field_id] = 1;
            BambooAPI.querySummary(chart.dataset_id, select, chart.y_field_id)
                .then(function (result) {
                    x_axis_keys.forEach(function (x_key, index) {
                        // TODO: pick a color from the d3 palette
                        var item = {key: x_key, color: colors[index], values: []};
                        y_axis_keys.forEach(function (y_key) {
                            // TODO: use info to get friendly names
                            var value = {
                                label: y_key,
                                value: result[chart.y_field_id][y_key][chart.x_field_id].summary[x_key] || 0
                            };
                            item.values.push(value);
                        });
                        items.push(item);
                    });
                    chart.data = items;
                });
        };

        $scope.chartData = function(chart) {
            return [{}];
        };

        $scope.refresh = function(chart) {
            chart.data = [];
        };

        $scope.msgs = [{id: 1, val: "Hello"}, {id: 2, val: "Goodbye"}];
        $scope.swapMessages = function(msg) {
            msg.val = msg.val === "Hello"?"Goodbye":"Hello";
        };
    }]);