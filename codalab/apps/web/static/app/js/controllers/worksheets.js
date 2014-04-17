'use strict';

angular.module('codalab.controllers')
    .controller('worksheets', ['$scope', 'worksheetsApi', function($scope, worksheetsApi) {
        $scope.status = 'loading';
        $scope.selectionIndex = 0;
        $scope.worksheets = [];

        $scope.statusMessage = function(status) {
            var messages = {
                '': '',
                'loading': 'Loading worksheets...',
                'loaderror': 'Couldn\'t retrive worksheets - Try refreshing the page',
                'empty': 'There are no worksheets.',
                'saving': 'Saving',
                'saveerror': 'Couldn\'t save - Try a different name'
            };
            switch (status) {
                case 'loaded':
                    return $scope.worksheets.length > 0 ? '' : messages['empty'];
            }
            return messages[status];
        };

        $scope.hasStatus = function(status) {
            return status && status.length > 0;
        };

        worksheetsApi.worksheets().then(function(worksheets) {
            $scope.status = 'loaded';
            angular.forEach(worksheets, function(worksheet) {
                worksheet.url = '/worksheets/' + worksheet.uuid;
                worksheet.target = '_self';
                worksheet.editable = false;
                $scope.worksheets.push(worksheet);
            });
        }, function() {
            $scope.status = 'loaderror';
        });

        $scope.saveWorksheet = function(worksheet) {
            worksheet.status = 'saving';
            worksheetsApi.createWorksheet(worksheet).then(function(createdWorksheet) {
                worksheet.uuid = createdWorksheet.uuid;
                worksheet.url = '/worksheets/' + worksheet.uuid;
                worksheet.editable = false;
                worksheet.target = '_self';
            }, function() {
                worksheet.status = 'saveerror';
            });
        };

        $scope.worksheetEnabled = function(worksheet) {
            return worksheet.name.length > 0;
        };

        $scope.addWorksheet = function(index, insertBellow) {
            $scope.selectionIndex = index + (insertBellow ? 1 : 0);
            $scope.worksheets.splice($scope.selectionIndex, 0, {
                'name': '',
                'editable': true,
                'url': '#'
            });
        };

        $scope.keyPressed = function(e) {
            if (e.ctrlKey) {
                switch (e.keyCode) {
                    case 38:
                    case 40: {
                        if ($scope.user.authenticated) {
                            var insertBellow = (e.keyCode === 40);
                            $scope.addWorksheet($scope.selectionIndex, insertBellow);
                            e.preventDefault();
                        }
                        break;
                    }
                }
            }
            else {
                switch (e.keyCode) {
                    // Move Up
                    case 38:
                        if ($scope.selectionIndex > 0) $scope.selectionIndex -= 1;
                        else $scope.selectionIndex = 0;
                        e.preventDefault();
                        break;
                    // Move Down
                    case 40:
                        if ($scope.selectionIndex < $scope.worksheets.length - 1) $scope.selectionIndex += 1;
                        else $scope.selectionIndex = $scope.worksheets.length - 1;
                        e.preventDefault();
                        break;
                }
            }
        };

        $scope.gotFocus = function(index) {
            $scope.selectionIndex = index;
        };

        $scope.lostFocus = function(index) {
            if ($scope.selectionIndex === index)
                $scope.selectionIndex = ($scope.selectionIndex === $scope.worksheets.length - 1) ? $scope.selectionIndex = $scope.worksheets.length : -1;
        };
    }]);
