-- ADVERTENCIA--
/* ESTO NO ES UN SCRIPT, es un documento de referencia entendible por el usuario
de como se ve aproximadamente la base de datos.
La base de datos es generada por django de forma automática y no es recomendable
alterar las tablas manualmente a menos que se sepa muy bien lo que se está haciendo. */

-- Tabla usuario generada automáticamente
CREATE TABLE _user(
    id UUID PRIMARY KEY DEFAULT get_random_uuid(),
    username VARCHAR NOT NULL UNIQUE,
    password CHAR NOT NULL, -- hasheado
    is_voluntario BOOLEAN DEFAULT false,
    is_organizador BOOLEAN DEFAULT false,
    email VARCHAR NOT NULL
);

-- Tabla voluntario con relación 1:1 con usuario
-- Los voluntarios seran capaces de darse de alta desde la pagina web
CREATE TABLE voluntario(
    user_id UUID PRIMARY KEY ,
    nombre VARCHAR NOT NULL, -- Nombre completo
    telefono CHAR(10) NOT NULL, -- Con lada, Sólo números 
    correo_electronico EMAIL NOT NULL UNIQUE,
    num_cuenta_unam CHAR(9) NOT NULL UNIQUE, -- Sólo números
    foto VARCHAR DEFAULT 'default.jpg', -- Un varchar que django interpreta como ruta a la imagen
    total_horas INT DEFAULT 0, -- Total horas de voluntariado
    FOREIGN KEY (user_id) REFERENCES _user (id)
);

-- Las instituciones deberan mandar una carta apropiada a la facultad de la UNAM para ser registradas
-- EL registro será creado manualmente por el DBA
-- La llave primaria de la institución será proporcionada a dicha institución por el DBA 
CREATE TABLE institucion(
    id UUID PRIMARY KEY DEFAULT get_random_uuid(),
    telefono CHAR(10) NOT NULL, -- Con lada, Sólo números 
    nombre VARCHAR(256) NOT NULL,
    direccion VARCHAR(300) NOT NULL,
    ciudad VARCHAR(256) NOT NULL,
    tipo_organizacion INT NOT NULL, -- Es int porque cada número es una 'Elección' de un diccionario. Ver 'django choices'
    url_pagina URL NOT NULL
);

-- Los organizadores pueden registrarse en la página web pero deben de proporcionar la llave primaria de la institución
-- La llave primaria se las proporcionará su institucion
CREATE TABLE organizador(
    user_id UUID PRIMARY KEY ,
    nombre VARCHAR(256) NOT NULL,
    telefono_movil CHAR(10) NOT NULL, -- Con lada, Sólo números
    telefono_oficina CHAR(10), -- Con lada, Sólo números
    correo_electronico EMAIL NOT NULL UNIQUE,
    password VARCHAR(72) NOT NULL,
    institucion_id UUID NOT NULL,
    foto VARCHAR DEFAULT 'default.jpg', -- Un varchar que django interpreta como ruta a la imagen
    FOREIGN KEY (institucion_id) REFERENCES institucion(id),
    FOREIGN KEY (user_id) REFERENCES _user(id),
);

-- Los eventos podrán ser creados unicamente por los organizadores mediante una interfaz web
CREATE TABLE evento(
    id UUID PRIMARY KEY DEFAULT get_random_uuid(),
    nombre VARCHAR(256) NOT NULL,
    fecha DATE NOT NULL,
    lugar VARCHAR(256) NOT NULL,
    activo BOOLEAN DEFAULT true, -- Los eventos 'activos' aparecen listados en las querys y permiten que los voluntarios se registren
    -- Es responsabilidad del organizador cambiarlo a 'inactivo' para cerrar las inscripciones a dicho evento
    -- Plan a futuro es programar que los eventos cambien automaticamente a inactivos despues de N dias.
    organizador_id UUID NOT NULL,
    descripcion TEXT NOT NULL,
    num_grupos INT NOT NULL DEFAULT 1, -- Numero de grupos que habra en el evento, es modificable
    url_pagina VARCHAR(300), -- url a la pagina del evento
    FOREIGN KEY (organizador_id) REFERENCES organizador(user_id)
);

-- Transitiva entre evento y voluntario, marca que un voluntario participo en dicho evento
-- Al finalizar un evento (cuando pasa a ser 'inactivo') tanto el voluntario como el organizador pueden realizar un comentario al respecto del otro.
-- A su vez al finalizar, el organizador debe reportar cuantas horas ayudó el voluntario.
-- IDEAS: Añadir rangos al contar el total de horas    eg. "Voluntario de oro" por juntar 100 horas

CREATE TABLE participacion(
    voluntario_id UUID NOT NULL,
    evento_id UUID NOT NULL,
    horas INT DEFAULT 0, -- empieza en 0, el organizador pone las horas participadas al final del evento
    comentario_voluntario TEXT, -- comentarios que se ponen al final
    comentario_organizador TEXT, -- comentarios que se ponen al final
    grupo INT NOT NULL DEFAULT 1, -- Numero del grupo al que pertenece al usuario en el evento (menor o igual al numero de grupos del evento)
    capitan BOOLEAN NOT NULL DEFAULT False, -- Determina si el voluntario es o no capitan
    FOREIGN KEY (evento_id) REFERENCES evento(id),
    FOREIGN KEY (voluntario_id) REFERENCES voluntario(user_id)
);
