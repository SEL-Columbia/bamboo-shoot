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
        $scope, $http, BambooAPI){
        // request a list of charts from the server
        var charts = [];
        // TODO: pick a color from the d3 palette
        var colors = ['#1f77b4', '#d62728'];
        $http({method: 'GET', url: charts_url}).
            success(function (data, status, headers, config) {
                $scope.charts = [
                    {
                        title: "Gender by Grade",
                        dataset_host_url: "http://192.168.56.2:8080",
                        dataset_id: "361bbd13d61c47718dd8e1ec36197acc",
                        type: "multiBarHorizontalChart",
                        x_field_id: "sex",
                        y_field_id: "grade"
                    },
                    {
                        title: "Income by Gender",
                        dataset_host_url: "http://192.168.56.2:8080",
                        dataset_id: "361bbd13d61c47718dd8e1ec36197acc",
                        type: "multiBarHorizontalChart",
                        x_field_id: "income",
                        y_field_id: "sex"
                    }
                ];
                // for each chart, get its bamboo data
                $scope.charts.forEach(function(chart){
                    bamboo.settings.URL = chart.dataset_host_url;

                    var select = {};
                    select[chart.x_field_id] = 1;
                    select[chart.y_field_id] = 1;
                    var promise = BambooAPI.querySummary(
                        chart.dataset_id, select);
                    promise.then(function(data){
                        var x_axis_keys = Object.keys(data[chart.x_field_id].summary);
                        var y_axis_keys = Object.keys(data[chart.y_field_id].summary);

                        //chart.data =
                        // TODO: create functions for the different chart types that convert bamboo data into target chart's format
                        var items = [];

                        // get grouped summarized data
                        select = {};
                        select[chart.x_field_id] = 1;
                        BambooAPI.querySummary(chart.dataset_id, select, chart.y_field_id)
                            .then(function(result){
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
                    });
                });
            }).
            error(function (data, status, headers, config) {

            });
        $scope.charts = charts;

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