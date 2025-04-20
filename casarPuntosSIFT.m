
function [puntosMatch] = casarPuntosSIFT(umbral1,umbral2,des1,loc1,des2,loc2)

%umbral1: Umbral para el error de correspondencia
%umbral2: Umbral para discernir con el segundo mejor casamiento

%Calcula la matriz traspuesta de des2
des2t = des2';                    

%Bucle para cada descriptor de la primera imagen
for i = 1 : size(des1,1)
    % Computes vector of dot products
    dotprods = des1(i,:) * des2t;    
    % Take inverse cosine and sort results
    [vals,indx] = sort(acos(dotprods)); 
    
    %Valores por defecto
    match(i) = 0;
      
    %Valor del angulos por debajo de un umbral
    if (vals(1) < umbral1 )
        % Check if nearest neighbor has angle less than distRatio times 2nd.
        if (vals(1) < umbral2 * vals(2))
            match(i) = indx(1);
        end
    end
   
end


%GENERA LA MATRIZ DE RESULTADOS
%Por filas los puntos casados
%Por columnas (x,y) primera imagen, (x,y) segunda imagen

%Numero de puntos casados
num = sum(match > 0);
puntosMatch=zeros(num,4);
indice=1;

%Bucle para cada caracteristica encontrada
for i = 1: size(des1,1)
    %Caracteristica casada
    if (match(i) > 0)
        puntosMatch(indice,1)=loc1(i,1);
        puntosMatch(indice,2)=loc1(i,2);
        puntosMatch(indice,3)=loc2(match(i),1);
        puntosMatch(indice,4)=loc2(match(i),2);
        indice=indice+1;
    end
end









