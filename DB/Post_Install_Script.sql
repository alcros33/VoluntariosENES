-- INFORMACION
/* Este script son detalles adicionales a nivel de base de datos que django no puede configurar tan facilmente
Contiene funciones, triggers y demas para ayudar al manejo de la misma,
Se debe ejecutar DESPUÉS de 'migrar' utilizando django */


-- Extension para criptografia
CREATE EXTENSION pgcrypto;

-- Random uuid como default
ALTER TABLE institucion ALTER COLUMN id SET DEFAULT gen_random_uuid();

-- ENES MORELIA
INSERT INTO institucion(nombre,telefono,ciudad,tipo_organizacion,url_pagina,direccion) VALUES
('Escuela Nacional de Estudios Superiores Unidad Morelia', '4436893500','Morelia',0,
'http://www.enesmorelia.unam.mx',
'Antigua Carretera a Pátzcuaro #8701,
Col. Ex Hacienda de San José de la Huerta,
C.P. 58190');

-- Trigger para sumar las horas
CREATE OR REPLACE FUNCTION sumar_horas() RETURNS TRIGGER AS $$
BEGIN
    UPDATE voluntario SET total_horas =  total_horas + (NEW.horas-OLD.horas) WHERE user_id = NEW.voluntario_id;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER actualizar_horas BEFORE UPDATE OF horas ON participacion
FOR EACH ROW
 EXECUTE PROCEDURE sumar_horas();

 -- IDEA ---
 -- Añadir una tabla que cuente las altas y bajas para fines estadísticos --
