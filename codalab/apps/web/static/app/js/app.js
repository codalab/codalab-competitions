'use strict';

angular.module('codalab.services', []);
angular.module('codalab.controllers', []);
angular.module('codalab.directives', []);

angular
    .module('codalab', [
        'ngRoute',
        'ngAnimate',
        'codalab.controllers',
        'codalab.services',
        'codalab.directives'
    ])
    .factory('$exceptionHandler', function() {
        return function(exception) {
            console.error(exception.message);
            error(exception);
        };
    })
    .config(['$routeProvider', '$locationProvider', '$httpProvider', function($routeProvider, $locationProvider, $httpProvider) {
        $routeProvider
            .when('/worksheets/app/:uuid/', {
                templateUrl: '/static/app/partials/worksheet.html',
                controller: 'worksheet'
            })
            .otherwise({
                templateUrl: '/static/app/partials/worksheets.html',
                controller: 'worksheets'
            });

        $locationProvider.html5Mode(true);
    }]);
