'use strict';

angular.module('codalab.services')
    .factory('worksheetsApi', ['$http', function ($http) {
        var csrfSafeMethod = function (method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        var sameOrigin = function (url) {
            // test that a given url is a same-origin URL
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }

        var success = function (result, status, headers, config) {
            return result.data;
        }
        var failure = function (result, status, headers, config) {
            throw result;
        }
        var apiCall = function (url) {
            return function () {
                return $http.get(url).then(success, failure);
            }
        }
        var apiPostCall = function (url) {
            return function (data) {
                // For CSRF + DJango see: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
                var csrftoken = $.cookie('csrftoken');
                if (!csrfSafeMethod("POST") && sameOrigin(url)) {
                    $http.defaults.headers.common["X-CSRFToken"] = csrftoken;
                }

                return $http.post(url, data).then(success, failure);
            }
        }
        var factory = {
            info: apiCall('/api/worksheets/info/'),
            worksheets: apiCall('/api/worksheets/'),
            createWorksheet: apiPostCall('/api/worksheets/'),
        }
        return factory;
    }]);