'use strict';

angular.module('codalab.directives')
    .directive('setFocus', function ($timeout) {
        return {
            scope: { trigger: '@setFocus' },
            link: function ($scope, element) {
                $scope.$watch('trigger', function (value) {
                    if (value === "true" && document.activeElement != element) {
                        var phase = $scope.$root.$$phase;
                        $timeout(function () {
                            if ($scope.trigger === "true") {
                                element[0].focus();
                                element[0].scrollIntoView();
                                $scope.trigger = false;
                            }
                        });
                    }
                });
            }
        };
    });