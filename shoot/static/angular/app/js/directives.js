'use strict';

/* Directives */


angular.module('BambooUI.directives', []).
    directive('appVersion', ['version', function (version) {
        return function (scope, elm, attrs) {
            elm.text(version);
        };
    }])
    .directive('shootChart', function () {
        var updateChart = function (newVal, oldVal, scope) {
            if (newVal !== oldVal) {
                nv.addGraph(function () {
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
            link: function (scope, element) {
                scope.element = element[0];
                scope.$watch('data', updateChart, false);
            }
        }
    })
    .directive('hasSelections', function () {
        var checkSelections = function (evt) {
            //var scope = evt.data.scope;
            if (this.checked)
                scope.has_field_selection = true;
            else
                scope.has_field_selection = $(scope.selector).length > 0;
        };

        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                scope.selector = attrs['hasSelections'];
                scope.onChangeHandler = attrs['onChange'];
                element.bind('change', function () {
                    var elm = this;
                    var value = elm.checked || $(scope.selector).length > 0;
                    var func = function () {
                        scope[scope.onChangeHandler](value);
                    };

                    if (!scope.$$phase) {
                        scope.$apply(func);
                    }
                    else {
                        func();
                    }
                });
            }
        }
    })
    .directive('triggerEvent', function () {
        return {
            scope: {
                model: '=ngModel'
            },
            link: function (scope, element, attrs) {
                scope.selector = attrs['selector'];
                scope.event = attrs['triggerEvent'];
                element.on('change', function () {
                    var checked = element.attr('value');
                    scope.$apply(function () {
                        scope.model = checked;
                    });
                });
                scope.$watch('model', function (newVal, oldVal, scope) {
                    if (newVal !== oldVal) {
                        $(scope.selector).trigger(scope.event);
                    }
                }, true);
            }
        }
    })
    .directive('helloDirective', function () {
        var updateMessage = function (newVal, oldVal, scope) {
            console.log(scope);
        };

        return {
            scope: { message: '=' },
            link: function (scope, iElement, iAttrs, controller) {
                scope.$watch('message', updateMessage, false);
            }
        }
    });
