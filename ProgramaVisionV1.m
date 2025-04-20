%% LÍNEAS PARA LA INICIALIZACIÓN DE LA CÁMARA 
imaqreset; % Reinicia el hardware de adquisición de video
disp(imaqhwinfo);

info = imaqhwinfo('winvideo'); % Cambia 'winvideo' si estás en Linux u otro sistema
disp(info.DeviceInfo); % Esto mostrará todas las cámaras detectadas

% Iniciar cámara
cam = videoinput('winvideo', 2); % Usa el ID correspondiente
set(cam, 'ReturnedColorSpace', 'rgb');

%% ALGORITMO DETECCIÓN DE VARIAS PIEZAS VISTAS POR LA CÁMARA Y CENTROIDE

% Captura la imagen desde la cámara
%AreaTrabajo = getsnapshot(cam); 
AreaTrabajo = imread("puzleVERDE.jpg");

ATgray = rgb2gray(AreaTrabajo);
ATbin = imbinarize(ATgray, 'global'); 
ATlabel = bwlabel(not(ATbin));

% Inicializar el array para los centroides
centroides = [];

figure()
imshow(label2rgb(ATlabel))
colormap(gca,[0 0 0;colorcube])
hold on

for k = 1:max(ATlabel(:))
    if bwarea(ATlabel == k) >= 900  % Filtrar por área mínima
        ob = (ATlabel == k);        % Máscara binaria del objeto con etiqueta k
        [y, x] = find(ob);          % Coordenadas de los píxeles del objeto
        cx = mean(x);               % Centroide X
        cy = mean(y);               % Centroide Y

        % Añadir el centroide al array
        centroides = [centroides; cx, cy];

        % Mostrar visualmente en la imagen
        plot(cx, cy, 'r*', 'MarkerSize', 10, 'LineWidth', 1.5)
        text(cx + 5, cy, sprintf('(%0.0f, %0.0f)', cx, cy), 'Color', 'r', 'FontSize', 12)
    end
end

%% ROBOT SE MUEVE A PIEZAS POR ORDEN SEGÚN CENTROIDES GUARDADOS

tamVentana = 100; % Tamaño de media ventana (ajústalo al tamaño típico de una pieza)

for i = 1:size(centroides, 1)
    cx = round(centroides(i,1));
    cy = round(centroides(i,2));

    % Definir los límites de la ventana con seguridad para no salirte de la imagen
    x1 = max(cx - tamVentana, 1);
    x2 = min(cx + tamVentana, size(AreaTrabajo, 2));
    y1 = max(cy - tamVentana, 1);
    y2 = min(cy + tamVentana, size(AreaTrabajo, 1));

    % Recorta la región de interés
    pieza = AreaTrabajo(y1:y2, x1:x2, :);

    % % Mostrar la pieza individual (o hacer análisis aquí)
    % figure
    % imshow(pieza)
    % title(sprintf('Pieza %d en (%d, %d)', i, cx, cy))

    % Aquí podrías hacer tu análisis: color, forma, comparación, etc.

    %%
    % Suponemos que ya tienes estas imágenes:
    % pieza: imagen de la pieza individual (recortada a partir del centroide)
    % AreaTrabajo: imagen completa del área de trabajo

    % Si no están en escala de grises, convertir
    if size(pieza, 3) == 3
        im1 = rgb2gray(pieza);
    else
        im1 = pieza;
    end

    if size(AreaTrabajo, 3) == 3
        im2 = rgb2gray(AreaTrabajo);
    else
        im2 = AreaTrabajo;
    end

    % Parámetros de matching
    MatchThreshold = 0.4;
    MaxRatio = 0.15;
    MatchThresholdHamming = 10.0;
    MaxRatioHamming = 0.4;

    %% ----------- SURF ----------------------
    fprintf('\nALGORITMO SURF\n');
    points1 = detectSURFFeatures(im1);
    [features1, validPoints1] = extractFeatures(im1, points1);

    points2 = detectSURFFeatures(im2);
    [features2, validPoints2] = extractFeatures(im2, points2);

    indexPairs = matchFeatures(features1, features2, ...
        'MaxRatio', MaxRatio, 'Unique', true, 'Metric', 'SSD', ...
        'MatchThreshold', MatchThreshold);

    matchedPoints1 = validPoints1(indexPairs(:,1), :);
    matchedPoints2 = validPoints2(indexPairs(:,2), :);

    figure;
    showMatchedFeatures(im1, im2, matchedPoints1, matchedPoints2, 'montage');
    title('SURF - Puntos casados');

    %% ----------- HARRIS ----------------------
    fprintf('\nALGORITMO HARRIS\n');
    points1 = detectHarrisFeatures(im1);
    [features1, validPoints1] = extractFeatures(im1, points1);

    points2 = detectHarrisFeatures(im2);
    [features2, validPoints2] = extractFeatures(im2, points2);

    indexPairs = matchFeatures(features1, features2, ...
        'MatchThreshold', MatchThresholdHamming, ...
        'MaxRatio', MaxRatioHamming, 'Unique', true);

    matchedPoints1 = validPoints1(indexPairs(:,1), :);
    matchedPoints2 = validPoints2(indexPairs(:,2), :);

    figure;
    showMatchedFeatures(im1, im2, matchedPoints1, matchedPoints2, 'montage');
    title('HARRIS - Puntos casados');

    %% ----------- SIFT (MATLAB) ----------------------
    fprintf('\nALGORITMO SIFT MATLAB\n');
    points1 = detectSIFTFeatures(im1);
    [features1, validPoints1] = extractFeatures(im1, points1);

    points2 = detectSIFTFeatures(im2);
    [features2, validPoints2] = extractFeatures(im2, points2);

    indexPairs = matchFeatures(features1, features2, ...
        'MaxRatio', 0.25, 'Unique', true, 'Metric', 'SSD', ...
        'MatchThreshold', 0.4);

    matchedPoints1 = validPoints1(indexPairs(:,1), :);
    matchedPoints2 = validPoints2(indexPairs(:,2), :);

    figure;
    showMatchedFeatures(im1, im2, matchedPoints1, matchedPoints2, 'montage');
    title('SIFT - Puntos casados');




end


