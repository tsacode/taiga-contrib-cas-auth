CasLoginButtonDirective = ($window, $params, $location, $config, $events, $confirm, $auth, $navUrls, $loader) ->
# Login or register a user with his/her cas account.
#
# Example:
#     tg-cas-login-button()
#
# Requirements:
#   - .....
  link = ($scope, $el, $attrs) ->
    auth_url = $config.get("casUrl", null)

    loginOnSuccess = (response) ->
      if $params.next and $params.next != $navUrls.resolve("login")
        nextUrl = $params.next
      else
        nextUrl = $navUrls.resolve("home")

      $events.setupConnection()

      $location.search("ticket", null)
      $location.path(nextUrl)

    loginOnError = (response) ->
      $loader.pageLoaded()

      if response.data._error_message
        $confirm.notify("light-error", response.data._error_message)
      else
        $confirm.notify("light-error", "Our Oompa Loompas have not been able to get you
                                                credentials from CAS.") #TODO: i18n

    loginWithCASAccount = ->
      ticket = $params.ticket

      return if not (ticket)
      $loader.start(true)

      url = document.createElement('a')
      url.href = $location.absUrl()
      redirectUri = "#{url.protocol}//#{url.hostname}#{if url.port == '' then '' else ':' + url.port}/login"
      currentLanguage = window.taigaConfig.defaultLanguage
      data = {ticket: ticket, redirectUri: redirectUri, currentLanguage : currentLanguage}
      $auth.login(data, "cas").then(loginOnSuccess, loginOnError)
    loginWithCASAccount()

    $el.on "click", ".button-auth", (event) ->
      url = document.createElement('a')
      url.href = $location.absUrl()
      redirectToUri = "#{url.protocol}//#{url.hostname}#{if url.port == '' then '' else ':' + url.port}/login"

      url = "#{auth_url}login?service=#{redirectToUri}"
      $window.location.href = url

    $scope.$on "$destroy", ->
      $el.off()

  return {
    link: link
    restrict: "EA"
    template: ""
  }

configure = ($translateProvider, $translatePartialLoaderProvider) ->
# i18n
  $translatePartialLoaderProvider.addPart('cas-auth')


module = angular.module('taigaContrib.casAuth', [])
module.directive("tgCasLoginButton", ["$window", '$routeParams', "$tgLocation", "$tgConfig", "$tgEvents",
  "$tgConfirm", "$tgAuth", "$tgNavUrls", "tgLoader",
  CasLoginButtonDirective])

module.config([
  "$translateProvider",
  "$translatePartialLoaderProvider",
  configure
])


