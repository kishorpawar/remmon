app.controller("ListServers", ['$rootScope', '$scope', '$http',
        function($rootScope, $scope, $http) 
        {
        	console.log("ListServers");

        	$scope.server_list = [];
        	$scope.formData = {
			    username: '',
			    password: '',
			    name: '',
			    ip_add: '',
			    port: 22,
        	}

			$scope.enroll_server = function(){
				$http({
					method : "post",
					url : 'servers/',
					data : $scope.formData,
					headers: {'Content-Type': 'application/x-www-form-urlencoded'}
				})
				.then(function success(data){
					console.log("SUCCESS ", data);
				},
				function error(error){
					console.log("ERROR ", error);
				});
			};

			$scope.get_server = function(){
				$http({
					method : "get",
					url : 'servers',
				})
				.then(function(success){
					console.log(success);
					$scope.server_list = success.data
				}, function(error){

				})
			}
        }
    ]);