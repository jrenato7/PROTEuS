var proEngApp = angular.module('proEngApp', ['ui.bootstrap']);

proEngApp.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

proEngApp.controller('proEngController', function($scope, $http, $location, $interval, $log, $uibModal, $anchorScroll){
    //$scope.linkacess = $location.absUrl();
    $scope.reload = function () {
        var url = $location.absUrl().split("/");
        var id_p = url[4].slice(0,64);
        $scope.linkacess = 'http://' + url[2] + '/' + url[3] + '/' + id_p ;
        $http.get("/process/" + id_p).success(function(data){
            //$scope.contacts = data['contacts'];
            var contacts = data['contacts'];
            var cttl = new Array();
            for(ct in contacts){

                tt = contacts[ct].title.split('-');
                nt = tt[0] + '/' + tt[1];
                var cts = new Array();
                for(k in contacts[ct].contacts){
                    m = contacts[ct].contacts[k];
                    var ntc = "";
                    if(tt[0][0] == m.r1[0])
                        ntc = ""; // "_/";
                    else
                        ntc = tt[0] + m.r1[0] ;//+ "/";
                    if(tt[1][0] == m.r2[0])
                        ntc = ntc ;//+ "_";
                    else if(ntc == "")
                        ntc =  tt[1] + m.r2[0];
                    else
                        ntc = ntc + "/" + tt[1] + m.r2[0];
                    lnk = m.pdbid + m.r1 + m.r2;
                    cts.push({mutation: ntc, link: lnk});
                }
                cttl.push({site: nt, mutations: cts});
            }
            if(cttl.length > 0)
                $scope.cttlok = 1;
            $scope.contactsList = cttl;
            $scope.contacts = contacts;
            if(data['ps'] == 1){
                $scope.p_status = data['ps'];
            };




            /*if(data['contacts'].length == 0){
                console.log("none");
                // verificar se nenhum valor estiver sido processado e exibir imagem 'loading'
            } else{
                console.log("ok");
            };*/
        });
    };
    $scope.reload();
    $interval($scope.reload, 500000);

    $scope.scrollTo = function (id) {
        $location.hash(id);
        $anchorScroll();
    };

    $scope.show = function ($id_ali, $w, $m1, $m2) {
    var modalInstance = $uibModal.open({
      animation: true,
      templateUrl: 'myModalContent.html',
      controller: 'PopulateModal',
      size: 'lg',
      resolve: {
        idal: function () {
          return $id_ali;
        },
        cttypes: function(){
            return [$w, $m1 +'-' + $m2];
        }
      }
    });

    /*modalInstance.result.then(function (selectedItem) {
      $scope.selected = selectedItem;
    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });*/
  };

});

proEngApp.controller('PopulateModal', function ($scope, $uibModalInstance, $http, $log, idal, cttypes) {
    $scope.wild = cttypes[0][0][0];
    $scope.mutation = cttypes[1];
    $http.get("/showalign/" + idal).success(function(data){
        if (data['e'] == 1){
            $scope.alignok = 1;
        } else{
            $scope.alignok = data['e'];
            let element = $('#showaligncontent'); //angular.element(document.getElementById('showaligncontent'));
            let config = { backgroundColor: 'white', backgroundOpacity : 0.1 };
            let viewer = $3Dmol.createViewer( element, config );
            $scope.download = data['f2'];

            $http.get(data['f1']).success(function(data){
                let v = viewer;
                modelo = v.addModel(data, 'pdb');
                v.setStyle({model: modelo}, {stick: {colorscheme: 'greenCarbon'}});
                v.zoomTo();
                v.render();
            });
            $http.get(data['f2']).success(function(data){
                let v = viewer;
                modelo2 = v.addModel(data, 'pdb');
                v.setStyle({model: modelo2}, {stick: {colorscheme: 'blueCarbon'}});
                v.zoomTo();
                v.render();
            });
    };

        });

    /*$scope.ok = function () {
        $uibModalInstance.close($scope.selected.item);
    };*/

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
    /*$scope.toggleLayout = function ($lyt) {
        $scope.style = $lyt;
    };*/
});
