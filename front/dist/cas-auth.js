angular.module("templates").run(["$templateCache", function($templateCache) {$templateCache.put("/plugins/cas-auth/cas-auth.html","\n<div tg-cas-login-button=\"tg-cas-login-button\"><a href=\"\" title=\"Enter with your CAS account\" class=\"button button-auth\"><img src=\"/plugins/cas-auth/images/telesante-logo.png\" width=\"18\" height=\"18\"/><span translate=\"CAS-AUTH.BUTTON_TEXT\"></span></a></div>");}]);
(function() {
  var CasLoginButtonDirective, configure, module;

  CasLoginButtonDirective = function($window, $params, $location, $config, $events, $confirm, $auth, $navUrls, $loader) {
    var link;
    link = function($scope, $el, $attrs) {
      var auth_url, loginOnError, loginOnSuccess, loginWithCASAccount;
      auth_url = $config.get("casUrl", null);
      loginOnSuccess = function(response) {
        var nextUrl;
        if ($params.next && $params.next !== $navUrls.resolve("login")) {
          nextUrl = $params.next;
        } else {
          nextUrl = $navUrls.resolve("home");
        }
        $events.setupConnection();
        $location.search("ticket", null);
        return $location.path(nextUrl);
      };
      loginOnError = function(response) {
        $loader.pageLoaded();
        if (response.data._error_message) {
          return $confirm.notify("light-error", response.data._error_message);
        } else {
          return $confirm.notify("light-error", "Our Oompa Loompas have not been able to get you credentials from CAS.");
        }
      };
      loginWithCASAccount = function() {
        var currentLanguage, data, redirectUri, ticket, url;
        ticket = $params.ticket;
        if (!ticket) {
          return;
        }
        $loader.start(true);
        url = document.createElement('a');
        url.href = $location.absUrl();
        redirectUri = url.protocol + "//" + url.hostname + (url.port === '' ? '' : ':' + url.port) + "/login";
        currentLanguage = window.taigaConfig.defaultLanguage;
        data = {
          ticket: ticket,
          redirectUri: redirectUri,
          currentLanguage: currentLanguage
        };
        return $auth.login(data, "cas").then(loginOnSuccess, loginOnError);
      };
      loginWithCASAccount();
      $el.on("click", ".button-auth", function(event) {
        var redirectToUri, url;
        url = document.createElement('a');
        url.href = $location.absUrl();
        redirectToUri = url.protocol + "//" + url.hostname + (url.port === '' ? '' : ':' + url.port) + "/login";
        url = auth_url + "login?service=" + redirectToUri;
        return $window.location.href = url;
      });
      return $scope.$on("$destroy", function() {
        return $el.off();
      });
    };
    return {
      link: link,
      restrict: "EA",
      template: ""
    };
  };

  configure = function($translateProvider, $translatePartialLoaderProvider) {
    return $translatePartialLoaderProvider.addPart('cas-auth');
  };

  module = angular.module('taigaContrib.casAuth', []);

  module.directive("tgCasLoginButton", ["$window", '$routeParams', "$tgLocation", "$tgConfig", "$tgEvents", "$tgConfirm", "$tgAuth", "$tgNavUrls", "tgLoader", CasLoginButtonDirective]);

  module.config(["$translateProvider", "$translatePartialLoaderProvider", configure]);

}).call(this);
