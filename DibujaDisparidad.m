function DibujaDisparidad(Puntos,im1,im2,representaImagen,titulo)

    %Numero de puntos totales
    numPuntos=size(Puntos,1);

    %Representa una sola imagen con puntos detectados
    if (representaImagen==1)
        im3=im1;
    else
        im3=im2;
    end

    % Show a figure with lines joining the accepted matches.
    figure('Position', [100 100 size(im3,2) size(im3,1)]);
    %figure();
    colormap('gray');
    imagesc(im3);
    title(titulo);
    hold on;

    for (i=1:numPuntos)
        if (representaImagen==1)
            posX=Puntos(i,1);
            posY=Puntos(i,2);
            posX2=Puntos(i,3);
            posY2=Puntos(i,4);
        else
            posX=Puntos(i,3);
            posY=Puntos(i,4);
            posX2=Puntos(i,1);
            posY2=Puntos(i,2);                    
        end           

        for (j=-2:2)
            line([posX-2 posX+2],[posY+j posY+j], 'Color', 'c');
        end
        line([posX posX2],[posY posY2], 'Color', 'b');
    end
        
    hold off;
    
    
end







