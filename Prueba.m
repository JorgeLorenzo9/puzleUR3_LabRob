
%CALCULO DE  CARACTERISTICAS VISUALES

%des1, des2:            Valores de los vectores decriptores
%features1, features2:  Valores de los vectores decriptores
%loc1, loc2:            Localizacion de las caracteristicas visuales


%Nombre de las imagenes
nombreImagen1='Imagen1.pgm';
nombreImagen2='Imagen2.pgm';

%Lee las imagenes (para  SIFT  no es necesario)
im1=imread(nombreImagen1);
im2=imread(nombreImagen2);

%Parametro casamiento para SIFT
MatchThresholdSIFT=0.4;
MaxRatioSIFT=0.25;

%Parametro casamiento para NO SIFT. Distancia euclidea
MatchThreshold=0.4;
MaxRatio=0.15;

%Parametro casamiento para NO SIFT. Distancia Hamming
MatchThresholdHamming=10.0;
MaxRatioHamming=0.4;

%ESTOS PARÁMETROS NO SON NECESARIAMENTE LOS MÁS ADECUADOS.
%SON PARÁMETROS DE DEMOSTRACIÓN.
%CADA APLICACIÓN PUEDE REQUERIR UNOS PARÁMETROS CONCRETOS
%SEGÚN LA DENSIDAD DE PUNTOS REQUERIDOS.




%------------- SIFT NO FUNCION MATLAB  ------------------------------

%ALGORITMO SIFT
fprintf('\nALGORITMO SIFT\n');
% Find SIFT keypoints for each image
fprintf('Puntos SIFT primera imagen\n');
[im1, des1, loc1] = sift(nombreImagen1);
fprintf('Puntos SIFT segunda imagen\n');
[im2, des2, loc2] = sift(nombreImagen2);

%Puntos ya detectados previamente
numSIFT_1=size(loc1,1);
numSIFT_2=size(loc2,1);

%Casa los puntos
[puntosMatchSIFT] = casarPuntosSIFT(MatchThresholdSIFT, ...
                                    MaxRatioSIFT, ...
                                    des1,loc1,des2,loc2);
                
%Numero de puntos
numSIFT_Casados=size(puntosMatchSIFT,1);
fprintf('Puntos SIFT casados %d\n',numSIFT_Casados);

%Dibuja los puntos casados correctamente y su disparidad
DibujaCasamiento(puntosMatchSIFT,im1,im2,'SIFT. Puntos casados');
DibujaDisparidad(puntosMatchSIFT,im1,im2,1,'SIFT. Disparidad Puntos casados');


%------------- SIFT MATLAB ------------------------------

%ALGORITMO SIFT MATLAB
fprintf('\nALGORITMO SIFT MATLAB\n');
%Puntos en la primera imagen
points1 = detectSIFTFeatures(im1,Sigma=1.6,NumLayersInOctave=3,EdgeThreshold=20,ContrastThreshold=0.0133);
[features1, validPoints1] = extractFeatures(im1, points1);
num1=validPoints1.Count;
fprintf('Puntos SIFT primera imagen %d\n',num1);
loc1=zeros(num1,2);
loc1(:,:)=validPoints1.Location(:,:);

%Puntos en la segunda imagen
points2 = detectSIFTFeatures(im2,Sigma=1.6,NumLayersInOctave=3,EdgeThreshold=20,ContrastThreshold=0.0133);
[features2, validPoints2] = extractFeatures(im2, points2);
num2=validPoints2.Count;
fprintf('Puntos SIFT segunda imagen %d\n',num2);
loc2=zeros(num2,2);
loc2(:,:)=validPoints2.Location(:,:);
    
%Casa los puntos
indexPairs = matchFeatures(features1,features2,'MaxRatio',MaxRatio,...
            'Unique',true,'Metric','SSD','MatchThreshold',MatchThreshold);

%Construye la matriz de puntos
puntosMatchSIFT=[validPoints1.Location(indexPairs(:,1),:) ...
                 validPoints2.Location(indexPairs(:,2),:)];

%Numero de puntos
numSIFT_Casados=size(puntosMatchSIFT,1);
fprintf('Puntos SIFT MATLAB casados %d\n',numSIFT_Casados);

%Dibuja los puntos casados correctamente y su disparidad
DibujaCasamiento(puntosMatchSIFT,im1,im2,'SIFT. Puntos casados');
DibujaDisparidad(puntosMatchSIFT,im1,im2,1,'SIFT. Disparidad Puntos casados');




%------------- SURF ------------------------------

%ALGORITMO SURF
fprintf('\nALGORITMO SURF\n');
%Puntos en la primera imagen
points1 = detectSURFFeatures(im1);
[features1, validPoints1] = extractFeatures(im1, points1);
num1=validPoints1.Count;
fprintf('Puntos SURF primera imagen %d\n',num1);
loc1=zeros(num1,2);
loc1(:,:)=validPoints1.Location(:,:);

%Puntos en la segunda imagen
points2 = detectSURFFeatures(im2);
[features2, validPoints2] = extractFeatures(im2, points2);
num2=validPoints2.Count;
fprintf('Puntos SURF segunda imagen %d\n',num2);
loc2=zeros(num2,2);
loc2(:,:)=validPoints2.Location(:,:);
    
%Casa los puntos
indexPairs = matchFeatures(features1,features2,'MaxRatio',MaxRatio,...
            'Unique',true,'Metric','SSD','MatchThreshold',MatchThreshold);

%Construye la matriz de puntos
puntosMatchSURF=[validPoints1.Location(indexPairs(:,1),:) ...
                 validPoints2.Location(indexPairs(:,2),:)];

%Numero de puntos
numSURF_Casados=size(puntosMatchSURF,1);
fprintf('Puntos SURF casados %d\n',numSURF_Casados);

%Dibuja los puntos casados correctamente y su disparidad
DibujaCasamiento(puntosMatchSURF,im1,im2,'SURF. Puntos casados');
DibujaDisparidad(puntosMatchSURF,im1,im2,1,'SURF. Disparidad Puntos casados');



%------------- KAZE ------------------------------

%ALGORITMO KAZE
%Similar a SURF, pero empleando la funcion
%   detectKAZEFeatures()
%Cuando se detectan muchos puntos, la función 
%   matchFeatures()
%puede dar problemas de falta de memoria




%------------- HARRIS ------------------------------

%ALGORITMO HARRIS
fprintf('\nALGORITMO HARRIS\n');
%Puntos en la primera imagen
corners1 = detectHarrisFeatures(im1);
[features1, validCorners1] = extractFeatures(im1, corners1);
num1=validCorners1.Count;
fprintf('Puntos HARRIS primera imagen %d\n',num1);
loc1=zeros(num1,2);
loc1(:,:)=validCorners1.Location(:,:);


%Puntos en la segunda imagen
corners2 = detectHarrisFeatures(im2);
[features2, validCorners2] = extractFeatures(im2, corners2);
num2=validCorners2.Count;
fprintf('Puntos HARRIS segunda imagen %d\n',num2);
loc2=zeros(num2,2);
loc2(:,:)=validCorners2.Location(:,:);


%Casa los puntos
indexPairs = matchFeatures(features1,features2,'MatchThreshold',...
             MatchThresholdHamming,'MaxRatio',MaxRatioHamming,...
             'Unique',true);

%Construye la matriz de puntos
puntosMatchHARRIS=[validCorners1.Location(indexPairs(:,1),:) ...
                   validCorners2.Location(indexPairs(:,2),:)];
              
%Numero de puntos
numHARRIS_Casados=size(puntosMatchHARRIS,1);
fprintf('Puntos HARRIS casados %d\n',numHARRIS_Casados);

%Dibuja los puntos casados correctamente y su disparidad
DibujaCasamiento(puntosMatchHARRIS,im1,im2,'HARRIS. Puntos casados');
DibujaDisparidad(puntosMatchHARRIS,im1,im2,1,'HARRIS. Disparidad Puntos casados');




%------------- BRISK ------------------------------

%ALGORITMO BRISK
%Similar a HARRIS, pero empleando la funcion
%   detectBRISKFeatures()



%------------- ORB ------------------------------

%ALGORITMO ORB
%Similar a HARRIS, pero empleando la funcion
%   detectORBFeatures()
%Cuando se detectan muchos puntos, la función 
%   matchFeatures()
%puede dar problemas de falta de memoria


