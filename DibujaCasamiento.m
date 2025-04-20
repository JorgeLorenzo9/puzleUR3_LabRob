function DibujaCasamiento(Puntos,im1,im2,titulo)

    %Numero de puntos totales
    numPuntos=size(Puntos,1);

    % Create a new image showing the two images side by side.
    % Select the image with the fewest rows and fill in enough empty rows
    %   to make it the same height as the other image.
    rows1 = size(im1,1);
    rows2 = size(im2,1);

    if (rows1 < rows2)
        im1(rows2,1) = 0;
    else
        im2(rows1,1) = 0;
    end

    % Now append both images side-by-side.
    im3 = [im1 im2];
    
    % Show a figure with lines joining the accepted matches.
    figure('Position', [100 100 size(im3,2) size(im3,1)]);
    %figure();
    colormap('gray');
    imagesc(im3);
    title(titulo);
    hold on;


    %Numero de columnas de la primera imagen
    cols1 = size(im1,2);
    
    %Bucle para caracteristica casada
    for (i=1:numPuntos)
        posX=Puntos(i,1);
        posY=Puntos(i,2);
        posX2=Puntos(i,3);
        posY2=Puntos(i,4);
 
        line([posX posX2+cols1], [posY posY2], 'Color', 'c');
    end
    hold off;
end








