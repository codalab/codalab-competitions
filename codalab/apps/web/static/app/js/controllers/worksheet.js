'use strict';

angular.module('codalab.controllers')
    .controller('worksheet', ['$scope', 'worksheetsApi', function ($scope, worksheetsApi) {
        $scope.status = "Loading worksheet...";
    }]);