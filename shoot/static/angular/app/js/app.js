'use strict';


// Declare app level module which depends on filters, and services
angular.module('BambooUI', ['ui.bootstrap', 'BambooUI.filters', 'BambooUI.services', 'BambooUI.directives', 'BambooUI.controllers']).
  config(['$routeProvider', '$dialogProvider', function($routeProvider, $dialogProvider) {
    //$routeProvider.when('/view1', {templateUrl: 'partials/partial1.html', controller: 'MyCtrl1'});
    //$routeProvider.when('/view2', {templateUrl: 'partials/partial2.html', controller: 'MyCtrl2'});
    //$routeProvider.otherwise({redirectTo: '/view1'});
    //$dialogProvider.options({backdropFade: false, dialogFade: false});
  }]);

/// add Object.keys for cross browser compatibility
if (!Object.keys) Object.keys = function(o) {
    if (o !== Object(o))
        throw new TypeError('Object.keys called on a non-object');
    var k = [], p;
    for (p in o) if (Object.prototype.hasOwnProperty.call(o, p)) k.push(p);
    return k;
}
