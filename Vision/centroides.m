% Leer imagen
img = imread('puzleAZUL2.jpg');

% Convertir a escala de grises
gray = rgb2gray(img);

% Detectar bordes (Canny funciona bien con formas rectas como cubos)
edges = edge(gray, 'Canny',0.19);
figure(1); imshow(edges);

%%

% Cerrar bordes para conectar los contornos
se = strel('square', 4);
closedEdges = imclose(edges, se);

% Rellenar formas cerradas
filled = imfill(closedEdges, 'holes');

% Eliminar objetos pequeños (ruido)
clean = bwareaopen(filled, 1500); % Ajusta este valor según el tamaño de los cubos

figure(2); imshow(clean);

%%

% Extraer propiedades: centroides y cajas delimitadoras
props = regionprops(clean, 'Centroid', 'BoundingBox');

% Mostrar imagen original con centroides
figure(3);
imshow(img);
hold on;
for k = 1:length(props)
    c = props(k).Centroid;
    plot(c(1), c(2), 'r+', 'MarkerSize', 15, 'LineWidth', 2);
    rectangle('Position', props(k).BoundingBox, 'EdgeColor', 'g', 'LineWidth', 2);
end
hold off;
