app.controller("ListServers", ['$rootScope', '$scope', '$http', '$state',
    function($rootScope, $scope, $http, $state) 
    {
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
				data : $.param($scope.formData),
				headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			})
			.then(function success(data){
				swal({
					title: "Success", 
					text : "Done", 
					type : 'success',
					confirmButtonText: "OK",
					},function(){
						console.log("REDIRECTING");
						$state.go('list');
					});
			},
			function error(error){
				swal("Error", "Something went wrong", 'error');
			});
		};

		$scope.get_server = function(){
			$http({
				method : "get",
				url : 'servers',
			})
			.then(function(success){
				$scope.server_list = success.data
			}, function(error){
				swal("Error", "Something went wrong", 'error');
			})
		}
    }
]);

app.controller("Details", ["$rootScope", '$scope', "$http", '$stateParams',
	function($rootScope, $scope, $http, $stateParams){

		$scope.ip_add = $stateParams.ip

		// GET DISK INFO
		$scope.getDisk = function () {
		    $http({
		    	method : 'get',
		    	url : 'server/getdisk/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function (data) {
		    	$scope.destroy_dataTable("get_disk");
		        var $filterPs = $("#filter-ps");
		        $filterPs.val("").off("keyup");
		        var psTable = $("#get_disk").dataTable({
		            aaData: data.data,
		            aoColumns: [
		                { sTitle: "FILESYSTEM" },
		                { sTitle: "SIZE" },
		                { sTitle: "USED" },
		                { sTitle: "AVAIL" },
		                { sTitle: "USE %" },
		                { sTitle: "MOUNTED" }
		            ],
		            bPaginate: false,
		            bFilter: true,
		            sDom: "lrtip",
		            bAutoWidth: false,
		            bInfo: false
		        }).fadeIn();
		        $filterPs.on("keyup", function () {
		            psTable.fnFilter(this.value);
		        });
		    }, function(error){
		    	swal("Error", "Something went wrong", 'error');
		    });
		};	

		// GET USERS
		$scope.getUsers = function () {
			$http({
		    	method : 'get',
		    	url : 'server/getusers/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function (data) {
		        $scope.destroy_dataTable("get_users");
		        var $filterPs = $("#filter-ps");
		        $filterPs.val("").off("keyup");
		        var psTable = $("#get_users").dataTable({
		            aaData: data.data,
		            aoColumns: [
		                { sTitle: "USER" },
		                { sTitle: "TTY" },
		                { sTitle: "LOOGED IN FROM",
		                    sDefaultContent: "unavailable" }
		            ],
		            aaSorting: [
		                [0, "desc"]
		            ],
		            bPaginate: true,
		            sPaginationType: "two_button",
		            bFilter: false,
		            bAutoWidth: false,
		            bInfo: false
		        }).fadeIn();
		        $filterPs.on("keyup", function () {
		            psTable.fnFilter(this.value);
		        });
		    }, function(error){
		    	swal("Error", "Something went wrong", 'error');
		    });
		};


		//NET STATS
		$scope.getNetstat = function () {
			$http({
		    	method : 'get',
		    	url : 'server/getnetstat/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function (result) {
		        $scope.destroy_dataTable("get_netstat");
		        var $filterPs = $("#filter-ps");
		        $filterPs.val("").off("keyup");
		        var psTable = $("#get_netstat").dataTable({
		            aaData: result.data,
		            aoColumns: [
		                { sTitle: "COUNT" },
		                { sTitle: "LOCAL IP" },
		                { sTitle: "LOCAL PORT" },
		                { sTitle: "FOREIGN" }
		            ],
		            bPaginate: true,
		            sPaginationType: "two_button",
		            bFilter: true,
		            sDom: "lrtip",
		            bAutoWidth: false,
		            bInfo: false
		        }).fadeIn();
		        $filterPs.on("keyup", function () {
		            psTable.fnFilter(this.value);
		        });
		    }, function(){
		    	swal("Error", "Something went wrong", 'error');
		    });
		};


		// RAM
		var mem_ctx = $("#memoryChart").get(0).getContext("2d");
        var memChart = new Chart(mem_ctx);
        $scope.getMemUsage = function(){
        	$http({
		    	method : 'get',
		    	url : 'server/memory/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function(result) {
                var options = {
                    animation : false,
                    pointDotRadius : 4,
                    scaleLabel : "<%=value%> Mb"
                }
                memChart.Line(result.data, options);
            }, function(error){
            	swal("Error", "Something went wrong", 'error');
            });
        };

        // CPU
        var cpu_ctx = $("#cpuuChart").get(0).getContext("2d");
        var cpuChart = new Chart(cpu_ctx);
        $scope.cpuUsage = function(){
        	$http({
		    	method : 'get',
		    	url : 'server/cpuusage/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function(result) {
                var options = {
                    percentageInnerCutout : 50,
                    segmentStrokeWidth : 0
                }
                cpuChart.Doughnut(result.data, options);
            }, function(error){
            	swal("Error", "Something went wrong", 'error');
            });
        };


        // Traffic Chart
        var trf_ctx = $("#trfChart").get(0).getContext("2d");
        var trfChart = new Chart(trf_ctx);
        $scope.traffic_usage = function(){
        	$http({
		    	method : 'get',
		    	url : 'server/gettraffic/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function(result) {
		    	var options = {
                    animation : false,
                    pointDotRadius : 2,
                    scaleLabel : "<%=value%>"
                }
                trfChart.Line(result.data, options);
            }, function(error){
            	swal("Error", "Something went wrong", 'error');
            });
        };

        //PROCESSES 
        $scope.getProc = function () {
        	$http({
		    	method : 'get',
		    	url : 'server/proc/',
		    	params : { ip_add : $scope.ip_add }
		    })
		    .then(function(result) {
		    	destroy_dataTable("get_proc");
		        var $filterPs = $("#filter-ps");
		        $filterPs.val("").off("keyup");
		        var psTable = $("#get_proc").dataTable({
		            aaData: result.data,
		            aoColumns: [
		                { sTitle: "USER" },
		                { sTitle: "PID" },
		                { sTitle: "%CPU" },
		                { sTitle: "%MEM" },
		                { sTitle: "VSZ" },
		                { sTitle: "RSS" },
		                { sTitle: "TTY" },
		                { sTitle: "STAT" },
		                { sTitle: "START" },
		                { sTitle: "TIME" },
		                { sTitle: "COMMAND" }
		            ],
		            bPaginate: true,
		            sPaginationType: "full_numbers",
		            bFilter: true,
		            sDom: "lrtip",
		            bAutoWidth: false,
		            bInfo: false
		        }).fadeIn();
		        $filterPs.on("keyup", function () {
		            psTable.fnFilter(this.value);
		        });
            }, function(error){
            	swal("Error", "Something went wrong", 'error');
            });
		};

        // If dataTable with provided ID exists, destroy it.
		$scope.destroy_dataTable = function(table_id) {
		    var table = $("#" + table_id);
		    var ex = document.getElementById(table_id);
		    if ($.fn.DataTable.fnIsDataTable(ex)) {
		        table.hide().dataTable().fnClearTable();
		        table.dataTable().fnDestroy();
		    }
		}

	}
]);