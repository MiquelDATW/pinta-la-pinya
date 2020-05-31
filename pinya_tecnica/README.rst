.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Pinya Tècnica
==============

Aquesta aplicació permet fer una gestió tècnica completa d'una colla muixeranguera

Installation
============

* contacts
* event
* hr_skill
* mm_hr_team
* mm_hr_nutrition
* pinya_complements

Configuration
=============

Una vegada instal·lat el mòdul només cal donar permisos als usuaris de l'àrea tècnica.

.. image:: /pinya_tecnica/static/description/tecnica_001.png
   :alt: Captura de pantalla dels permisos de pinya
   :width: 90%

* Vés a Configuració > Usuaris i empreses > Usuaris
* Selecciona l'usuari i vés a Permisos d'accés > Application Accesses
* Edita
* Selecciona "Responsable pinya" en l'opció "Pinya"
* Desa

Usage
=======

Gasta l'assistent per crear les persones muixerangueres
-------------------------------------------------------

.. image:: /pinya_tecnica/static/description/tecnica_002_003.png
   :alt: Captura de pantalla de l'assistent de crear membre
   :width: 90%


Es pot accedir des de:

* Contactes > Contactes > Crear Membre
* Recursos Humans > Empleats > Crear Membre

Crea una àrea tècnica
---------------------

.. image:: /pinya_tecnica/static/description/tecnica_004.png
   :alt: Captura de pantalla de creació d'un equip
   :width: 90%

Quan tingues les muixerangueres creades pots donar d'alta l'equip de l'Àrea Tècnica

* Vés a Recursos Humans > Empleats > Equips
* Crea
* Nombra l'àrea tècnica
* Selecciona el Manager --> serà el mestre/a
* Marca el camp "Àrea Tècnica" ✔
* Selecciona la resta de l'equip
* Desa

Crea una temporada muixeranguera
--------------------------------

.. image:: /pinya_tecnica/static/description/tecnica_005.png
   :alt: Captura de pantalla de creació d'una temporada muixeranguera
   :width: 90%

Per a poder crear un assaig cal tindre una temporada muixeranguera activa.

* Vés a Enfaixa't > Enfaixa't > Temporades
* Crea
* Nombra la temporada
* Selecciona la data d'inici i de final
* Marca el camp "Actual" ✔
* Desa

Crea un assaig o una actuació
-----------------------------

.. image:: /pinya_tecnica/static/description/tecnica_006.png
   :alt: Captura de pantalla de creació d'un assaig
   :width: 90%

Ara ja es pot crear un assaig o una actuació❗

* Vés a Enfaixa't > Enfaixa't > Assajos o Enfaixa't > Enfaixa't > Actuacions
* Crea
* Nombra l'assaig o l'actuació
* Selecciona les dates d'inici i de final
* Si l'actuació forma part d'una Trobada o un Aplec, pots introduir-ho en Esdeveniment
* Desa

Selecciona les figures i les persones
-------------------------------------

.. image:: /pinya_tecnica/static/description/tecnica_007.png
   :alt: Captura de pantalla d'un assaig
   :width: 90%

Abans de calcular les muixerangues cal saber:

Quines persones vindran a l'assaig?

* Selecciona "Importar membres" i carrega les persones inscrites en el formulari d'assaig
* Si la teua colla gasta la web d'autoinscripció, les mateixes muixerangueres aniran apuntant-se a l'assaig i no caldrà importar cap document

Quines figures són possibles?

* Selecciona "Afegir muixerangues" i tria les figures i el número que vols fer


Ara ja podem calcular les persones que ocuparan les posicions de la muixeranga❗
-------------------------------------------------------------------------------

.. image:: /pinya_tecnica/static/description/tecnica_008.png
   :alt: Captura de pantalla d'un assaig
   :width: 90%


Bàsicament tenim 3 possibilitats

* Apretar el botó "Calcular muixeranga" i deixar que el programa decidisca l'alineació
* Omplir les posicions manualment
* Fer una mescla, per exemple omplir posicions que creiem clau i deixar que el programa faça la resta

Si vols editar manualment la figura, caldrà fer-ho d'alguna d'aquestes dues maneres:

* Apretar el botó "Editar" i anar a la pestanya de "Tronc" o de "Pinya" de la mateixa pàgina
* Apretar el botó "Tronc" o "Pinya" de la banda dreta i anar a una altra pàgina

El que recomanem és gastar els botons de la caixa d'icones de la banda dreta: Tronc i Pinya

* Cadascun dels botons ens durà a una nova pàgina com es mostra en la imatge
* Polsant l'última columna "Membre Tronc Level" s'ens obrirà un desplegable
* Junt al nom de les persones, hi ha unes estreles que representen el nivell de tècnica de la persona en la posició donada
* Les persones han sigut ordenades de major tècnica (més estreles) a menor tècnica (menys estreles)
* La dificultat estimada de la posició es veu en la columna "Tècnica"
* Així doncs, si s'ompli la posició manualment, és perfectament possible seleccionar gent de qualsevol nivell de tècnica

❗ Atenció. El camp "Alineació" és un desplegable que permet dir-li al programa quin percentatge de persones noves amb menys experiència en les figures cal que incloga en les posicions.

Pot variar entre

* **"Millor alineació"** on totes les posicions són ocupades per les persones més experimentades
* **"Tothom nou"** on les persones tenen la tècnica necessària, però mai han ocupat eixa posició

Pots omplir el camp "Mestra" amb la persona de l'àrea tècnica que s'encarregarà de cantar la figura. Previàment caldrà haver definit l'equip de l'àrea tècnica.


Acaba de preparar la muixeranga
-------------------------------

Quan les posicions de la figura s'han omplit, cal que hi passe d'estat

Què vol dir passar d'estat?

Vol dir que deixarà d'estar en "Esborrany" i passarà a estar "Preparada"

Hi ha 6 possibles estats que marquen l'estat (mai millor dit) de la figura

* "Esborrany": la figura està sense una alineació encara
* "Preparada": la figura s'han calculat totes les posicions i està llesta per ser assajada o duta a plaça
* "Descarregada": el que totes i tots volem per a les muixerangues, la figura s'ha muntat i completat sense cap incident
* "Intentada": aquest estat indica que la figura s'ha iniciat a muntar, però algun problema ha fet que es desmunte sense caure
* "Caiguda": el que ninguna volem per a les muixerangues, la figura ha caigut, indiferentment de si la xicalla l'havia coronada o no
* "Canceŀlada": la figura no s'ha probat de fer a l'assaig o a l'actuació


.. image:: /pinya_tecnica/static/description/tecnica_009.png
   :alt: Captura de pantalla dels estats d'un assaig
   :width: 50%

Els estats "Descarregada", "Intentada", "Caiguda" i "Canceŀlada" es gestionen des de la vista de les muixerangues, però per a poder accedir a eixos estats, l'assaig o actuació on està la figura cal que estiga en estat "Fet".


Credits
=======

All emojis designed by `OpenMoji <https://openmoji.org/>`__ – the open-source emoji and icon project. License: `CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>`__

Contributors
------------

* Miquel March <m.marchpuig@gmail.com>

Maintainer
----------

`MiquelDATW <https://github.com/MiquelDATW/pinta-la-pinya>`__
-------------------------------------------------------------




