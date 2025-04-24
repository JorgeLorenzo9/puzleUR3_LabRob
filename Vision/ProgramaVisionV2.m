close all; clear all; clc;

%% LÍNEAS PARA LA INICIALIZACIÓN DE LA CÁMARA 
imaqreset; % Reinicia el hardware de adquisición de video
disp(imaqhwinfo);

info = imaqhwinfo('winvideo'); % Cambia 'winvideo' si estás en Linux u otro sistema
disp(info.DeviceInfo); % Esto mostrará todas las cámaras detectadas

% Iniciar cámara
cam = videoinput('winvideo', 2); % Usa el ID correspondiente
set(cam, 'ReturnedColorSpace', 'rgb');

figure()
imshow(getsnapshot(cam));

%%
%AreaRecogida = getsnapshot(cam);
AreaRecogida = imread("random1.jpg");

figure(1); imshow(AreaRecogida);
%%
% Definir el rectángulo de recorte [xmin, ymin, ancho, alto]
rect = [350, 32, 1114, 769]; 

% Aplicar crop
%img_crop = imcrop(AreaRecogida, rect);
img_crop = AreaRecogida;


%figure(1); imshow(AreaRecogida);
figure(1); imshow(img_crop);

AreaRecogida_gray = rgb2gray(img_crop);
%AreaRecogida_hsv = rgb2hsv(img_crop);
AreaRecogida_YCbCr = rgb2ycbcr(img_crop);


% figure(2); 
% subplot(2,2,1)
% imshow(AreaRecogida_hsv);
% subplot(2,2,2)
% imshow(AreaRecogida_hsv(:,:,1));
% subplot(2,2,3)
% imshow(AreaRecogida_hsv(:,:,2));
% subplot(2,2,4)
% imshow(AreaRecogida_hsv(:,:,3));

%canal_h = AreaRecogida_hsv(:,:,2);
canal_h = AreaRecogida_YCbCr(:,:,3);

se = strel('disk', 6); % Elemento estructurante circular de radio 2
im_erode = imerode(canal_h, se); % Función correcta es imdilate

se2 = strel('disk',5);
im_fill = imerode(im_erode, se2); % Función correcta es imdilate

figure(3); 
subplot(1,2,1)
imshow(im_erode);
subplot(1,2,2)
imshow(im_fill);

im_canny = edge(im_fill, 'Canny',0.19);

figure(4)
imshow(im_canny);

im_bin = imbinarize(im_fill, 0.5);

ATlabel = bwlabel(im_bin);  % Equivalente a bwlabel(not(ATbin))
figure(5); imshow(label2rgb(ATlabel)); title('Etiquetado');


% Inicializar el array para los centroides
centroides = [];


figure()
imshow(label2rgb(ATlabel))
colormap(gca,[0 0 0;colorcube])
hold on

for k = 1:max(ATlabel(:))
    if bwarea(ATlabel == k) >= 1500  % Filtrar por área mínima
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