'use strict';

angular.module('codalab.directives')
    .directive('shortcut', function() {
        return {
            restrict: 'E',
            replace: true,
            scope: true,
            link: function postLink($scope, iElement, iAttrs) {
                var keyHandler = function(e) {
                    $scope.$apply($scope.keyPressed(e));
                };
                $(document).on('keydown', keyHandler);
                $scope.$on('$destroy', function() {
                    $(document).off('keydown', keyHandler);
                });
            }
        };
    });
