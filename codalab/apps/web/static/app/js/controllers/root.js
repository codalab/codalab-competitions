'use strict';

angular.module('codalab.controllers')
    .controller('root', ['$scope', 'worksheetsApi', function($scope, worksheetsApi) {
        worksheetsApi.info().then(function(info) {
            $scope.config = info.config;
            $scope.user = info.user;
        });
    }]);
