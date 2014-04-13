'use strict';

angular.module('codalab.services')
    .factory('worksheetsApi', ['$http', function($http) {
        var success = function(result, status, headers, config) {
            return result.data;
        };
        var failure = function(result, status, headers, config) {
            throw result;
        };
        var apiCall = function(url) {
            return function() {
                return $http.get(url).then(success, failure);
            }
        };
        var apiPostCall = function(url) {
            return function(data) {
                // For CSRF + DJango see: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
                var csrftoken = $.cookie('csrftoken');
                if (!csrfSafeMethod('POST') && sameOrigin(url)) {
                    $http.defaults.headers.common['X-CSRFToken'] = csrftoken;
                }

                return $http.post(url, data).then(success, failure);
            }
        };
        var factory = {
            info: apiCall('/api/worksheets/info/'),
            worksheets: apiCall('/api/worksheets/'),
            createWorksheet: apiPostCall('/api/worksheets/')
        };
        return factory;
    }]);
