angular.module('donde', [])
.controller('titulos', function($scope, $http){
    $http.get('http://127.0.0.1:5000/noticias/')
        .then(function(response){
            $scope.titulos = response.data.titulos;
        });

    $scope.noticia = [];
    $scope.cargar = function(id){
        $http.get('http://127.0.0.1:5000/noticias/'+id)
            .then(function(response){
                $scope.noticia.push(response.data.noticia)
                
            })
    }
}) ;
