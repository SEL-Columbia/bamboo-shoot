'use strict';

/* Directives */


angular.module('BambooUI.directives', []).
    directive('appVersion', ['version', function (version) {
        return function (scope, elm, attrs) {
            elm.text(version);
        };
    }])
    .directive('shootChart', function () {
        var updateChart = function(newVal, oldVal, scope){
            if(newVal !== oldVal)
            {
                nv.addGraph(function() {
                    var chart = nv.models.multiBarHorizontalChart()
                            .x(function (d) {
                                return d.label
                            })
                            .y(function (d) {
                                return d.value
                            })
                            .margin({top: 30, right: 20, bottom: 50, left: 175})
                            .showValues(true)
                            .tooltips(false)
                            .showControls(false);

                    chart.yAxis
                            .tickFormat(d3.format(',.2f'));

                    d3.select(scope.element)
                            .datum(newVal)
                            .transition().duration(500)
                            .call(chart);

                    nv.utils.windowResize(chart.update);

                    return chart;
                });
            }
        };

        return {
            scope: { data: '=' },
            link: function (scope, iElement, iAttrs, controller) {
                scope.element = iElement[0];
                scope.$watch('data', updateChart, false);
            }
        }
    })
    .directive('helloDirective', function(){
        var updateMessage = function(newVal, oldVal, scope) {
            console.log(scope);
        };

        return {
            scope: { message: '=' },
            link: function (scope, iElement, iAttrs, controller) {
                scope.$watch('message', updateMessage, false);
            }
        }
    });
