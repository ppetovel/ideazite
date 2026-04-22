Es algo complidado bajar, pero basta con hacer correr el python 

Clio_scraper_clean_v6.py

Tarda basnate, como tres horas mas o menos para un año.
lo deja muy bien, despues lo limpias como siempre


PRIMERO hay que copiar una cookie

Para el caso de los clio sports:
Abrí en tu navegador https://clios.com/winners-gallery/explore?vertical=Clio+Sports&season=2025
estando logueado.

Entrá a las herramientas de desarrollador → 
ACTUALIZAR LA PAGINA
pestaña APLICATION
COOKIES
nemo_token (HAY QUE COPIAR el numero largo ese es la cookie, SÓLO EL NUMERO LARGO)

A todo ese valor lo pegas en el archivo cookie.txt
sólo el valor, nada más, 
en una sola línea, sin espacios ni saltos.

Antes de hacer correr el script hay que cambiar dos cosas, 
1 la página que va a scrapear, en el caso de clio awards 2026 era esta:
https://clios.com/winners-gallery/explore?vertical=Clio+Awards&season=2026&page_number={page}

se pega acá al comienzo donde esta ña base explore

BASE_EXPLORE = "https://clios.com/winners-gallery/explore?vertical=Clio+Awards&season=2026&page_number={page}"



Con Clio_entertainment es exactamenbte igual, pero con el script respecivo
Con clio awards, lo mismo

