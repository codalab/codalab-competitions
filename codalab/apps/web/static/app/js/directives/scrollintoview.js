'use strict';

angular.module('codalab.directives')
    .directive('scrollIntoView', ['$timeout', function($timeout) {
        return {
            scope: {
                trigger: '@scrollIntoView'
            },
            restrict: 'A',
            link: function($scope, element, attrs) {
                attrs.$observe('scrollIntoView', function(value, oldvalue) {
                    if (value === 'true' && value !== oldvalue) {
                        $timeout(function() {
                            if ($scope.trigger === 'true') {
                                element[0].scrollIntoView();
                                $scope.trigger = false;
                            }
                        });
                    }
                });
            }
        };
    }]);
