'use strict';

angular.module('codalab.directives')
    .directive('setFocus', ['$timeout', function($timeout) {
        return {
            scope: {
                trigger: '@setFocus'
            },
            restrict: 'A',
            link: function($scope, element, attrs) {
                attrs.$observe('setFocus', function(value) {
                    if (value === 'true' && document.activeElement != element) {
                        $timeout(function() {
                            if ($scope.trigger === 'true') {
                                element[0].focus();
                                $scope.trigger = false;
                            }
                        });
                    }
                });
            }
        };
    }]);
