var app = angular.module('remmon', [
    'ui.router',
    // 'ui.materialize',
    'ngRoute',
]);

app.run(function($rootScope) {
    $rootScope.$on("$stateChangeError", console.log.bind(console));
});


app.config(['$stateProvider', '$urlRouterProvider',
    function($stateProvider, $urlRouterProvider,) {

        // RestangularProvider.setDefaultHeaders({
        //     "X-CSRFToken": csrftoken
        // });
        $urlRouterProvider.otherwise("/");

        $stateProvider
        	.state("/", {
                url: "/",
                templateUrl: "/static/ng_templates/list_servers.html",
                controller: 'ListServers'
            })
            .state("details", {
                url : "/details/:ip",
                templateUrl : "/static/ng_templates/details.html",
                controller : 'Details'
            })
  	}]);

