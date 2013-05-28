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

    }]);